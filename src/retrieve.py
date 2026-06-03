import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

def get_retriever(collection_name: str = "enterprise_docs"):
    """Connect to existing ChromaDB collection."""
    client = chromadb.PersistentClient(path="chroma_db/")
    embedding_function = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_collection(
        name=collection_name,
        embedding_function=embedding_function
    )
    return collection

def retrieve_chunks(query: str, top_k: int = 5):
    """Find top K most relevant chunks for a given query."""
    collection = get_retriever()
    
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]
    
    print(f"\nQuery: {query}")
    print(f"Top {top_k} relevant chunks:\n")
    for i, (chunk, metadata) in enumerate(zip(chunks, metadatas)):
        print(f"--- Chunk {i+1} ---")
        print(f"Source: {metadata.get('source', 'Unknown')}")
        print(f"Content: {chunk[:200]}\n")
    
    return chunks, metadatas

if __name__ == "__main__":
    retrieve_chunks("What is model evaluation?")