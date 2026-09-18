import os
import chromadb

def get_chroma_client():
    host = os.getenv("CHROMA_HOST", "localhost")
    port = os.getenv("CHROMA_PORT", "8000")
    
    # We use the HTTP client to connect to the docker container
    client = chromadb.HttpClient(host=host, port=port)
    return client
