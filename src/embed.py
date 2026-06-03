import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from src.ingest import load_documents, chunk_documents

load_dotenv()

def get_embedding_function():
    """Use ChromaDB's built-in embedding function."""
    return embedding_functions.DefaultEmbeddingFunction()

def embed_and_store(chunks, collection_name: str = "enterprise_docs"):
    """Embed chunks and store in ChromaDB."""
    client = chromadb.PersistentClient(path="chroma_db/")
    
    embedding_function = get_embedding_function()
    
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )

    documents = [chunk.page_content for chunk in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [chunk.metadata for chunk in chunks]

    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )

    print(f"Stored {len(chunks)} chunks in ChromaDB collection '{collection_name}'")
    return collection

if __name__ == "__main__":
    docs = load_documents()
    chunks = chunk_documents(docs)
    collection = embed_and_store(chunks)
    print(f"Total documents in collection: {collection.count()}")