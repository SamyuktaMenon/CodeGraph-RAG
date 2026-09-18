from backend.db_chroma import get_chroma_client
from backend.db_neo4j import get_neo4j_driver
from sentence_transformers import SentenceTransformer, CrossEncoder
from typing import List, Dict

class HybridRetriever:
    def __init__(self):
        self.chroma_client = get_chroma_client()
        self.collection = self.chroma_client.get_or_create_collection("code_nodes")
        # Free local embedding model - same as used in ingestion
        self.embeddings = SentenceTransformer("all-MiniLM-L6-v2")
        self.neo4j_driver = get_neo4j_driver()
        # Initialize BGE-Reranker for the two-stage retrieval
        self.reranker = CrossEncoder("BAAI/bge-reranker-base")

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        # 1. Vector Search
        query_embedding = self.embeddings.encode(query).tolist()
        vector_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2 # fetch more for reranking
        )
        
        # 2. Graph Search (Structural context)
        graph_results = []
        try:
            with self.neo4j_driver.session() as session:
                # Basic search: Find entities with matching names or related entities
                res = session.run(
                    "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($q) "
                    "MATCH (n)-[r]-(m) "
                    "RETURN n.name, type(r), m.name, n.file_path LIMIT 5",
                    q=query
                )
                for record in res:
                    graph_results.append(
                        f"Graph Info: {record['n.name']} in {record['n.file_path']} "
                        f"has relationship {record['type(r)']} with {record['m.name']}"
                    )
        except Exception as e:
            print(f"Warning: Graph search failed (is Neo4j running?): {e}")

        # Combine results
        combined_docs = []
        if vector_results and vector_results['documents']:
            combined_docs.extend(vector_results['documents'][0])
            
        combined_docs.extend(graph_results)
            
        if not combined_docs:
            return []

        # 3. Two-stage Reranking
        pairs = [[query, doc] for doc in combined_docs]
        scores = self.reranker.predict(pairs)
        
        # Sort by score
        scored_docs = sorted(zip(combined_docs, scores), key=lambda x: x[1], reverse=True)
        
        # Return top_k
        return [{"content": doc, "score": float(score)} for doc, score in scored_docs[:top_k]]
