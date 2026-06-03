import sys
from dotenv import load_dotenv
from src.ingest import load_documents, chunk_documents
from src.embed import embed_and_store
from src.answer import answer_question

load_dotenv()

def build_pipeline():
    """Run the full ingestion pipeline - load, chunk, embed, store."""
    print("=== Building RAG Pipeline ===\n")
    docs = load_documents()
    chunks = chunk_documents(docs)
    embed_and_store(chunks)
    print("\n=== Pipeline Ready ===\n")

def ask(query: str):
    """Ask a question against the pipeline."""
    return answer_question(query)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If a question is passed as argument, answer it
        query = " ".join(sys.argv[1:])
        ask(query)
    else:
        # Otherwise build the pipeline
        build_pipeline()