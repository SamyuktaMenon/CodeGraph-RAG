from backend.db_chroma import get_chroma_client
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

class VectorIndexer:
    def __init__(self, collection_name: str = "code_nodes"):
        self.client = get_chroma_client()
        self.collection = self.client.get_or_create_collection(name=collection_name)
        # Free local embedding model - no API key needed
        self.embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")

    def index_nodes(self, nodes: List[Dict[str, Any]]):
        documents = []
        metadatas = []
        ids = []

        for i, node in enumerate(nodes):
            # Construct a self-contained document chunk for vector retrieval
            doc_text = f"File Path: {node.get('file_path')}\n"
            doc_text += f"Entity Type: {node.get('type')}\n"
            doc_text += f"Entity Name: {node.get('name')}\n"
            
            if node.get("docstring"):
                doc_text += f"Docstring:\n{node.get('docstring')}\n"
                
            if node.get("code"):
                doc_text += f"Source Code:\n{node.get('code')}\n"
            else:
                doc_text += f"Summary: {node.get('docstring', 'No code body captured')}\n"

            documents.append(doc_text)
            metadatas.append({
                "name": str(node.get("name")),
                "type": str(node.get("type")),
                "file_path": str(node.get("file_path")),
                "line_number": int(node.get("line_number", 0))
            })
            ids.append(f"{node.get('file_path')}_{node.get('name')}_{i}")

        if documents:
            # Generate embeddings locally and add to Chroma
            embeddings = self.embeddings_model.encode(documents).tolist()
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Indexed {len(documents)} documents into ChromaDB.")

if __name__ == "__main__":
    # Test execution block
    indexer = VectorIndexer()
    print("VectorIndexer initialized successfully.")