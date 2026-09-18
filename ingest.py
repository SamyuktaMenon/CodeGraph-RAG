import os
from dotenv import load_dotenv

# Load environment variables (OPENAI_API_KEY, NEO4J_URI, etc)
load_dotenv()

from ingestion.parser import PythonCodeParser
from ingestion.graph_builder import KnowledgeGraphBuilder
from ingestion.vector_indexer import VectorIndexer

def main():
    repo_path = "."
    print(f"Starting ingestion for repository at: {repo_path}")
    
    # 1. Parse Code
    print("Parsing Python files...")
    parser = PythonCodeParser(repo_path)
    parsed_data = parser.parse_repo()
    nodes = parsed_data.get("nodes", [])
    relationships = parsed_data.get("relationships", [])
    print(f"Found {len(nodes)} entities and {len(relationships)} relationships.")
    
    if not nodes:
        print("No Python nodes found to ingest.")
        return

    # 2. Populate Neo4j Graph
    print("Populating Knowledge Graph in Neo4j...")
    try:
        graph_builder = KnowledgeGraphBuilder()
        graph_builder.build_graph(nodes, relationships)
        graph_builder.close()
        print("Knowledge Graph updated successfully.")
    except Exception as e:
        print(f"Failed to populate Neo4j (is it running?): {e}")

    # 3. Populate ChromaDB Vector Store
    print("Populating Vector Database in ChromaDB...")
    try:
        if not os.getenv("OPENAI_API_KEY"):
            print("Warning: OPENAI_API_KEY is not set. Vector ingestion might fail.")
            
        vector_indexer = VectorIndexer()
        vector_indexer.index_nodes(nodes)
        print("Vector Database updated successfully.")
    except Exception as e:
        print(f"Failed to populate ChromaDB: {e}")

    print("Ingestion pipeline completed.")

if __name__ == "__main__":
    main()
