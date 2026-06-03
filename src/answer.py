import os
from dotenv import load_dotenv
import anthropic
from src.retrieve import retrieve_chunks

load_dotenv()

def answer_question(query: str):
    """Retrieve relevant chunks and answer using Claude."""
    
    # Step 1: Retrieve relevant chunks
    chunks, metadatas = retrieve_chunks(query, top_k=5)
    
    # Step 2: Build context from chunks
    context = ""
    sources = []
    for i, (chunk, metadata) in enumerate(zip(chunks, metadatas)):
        context += f"\n[Source {i+1}: {metadata.get('source', 'Unknown')}]\n{chunk}\n"
        sources.append(metadata.get('source', 'Unknown'))
    
    # Step 3: Build grounding prompt
    prompt = f"""You are an enterprise document assistant. 
Answer the question below using ONLY the context provided.
If the answer is not in the context, say "I don't have enough information in the provided documents to answer this question."
Always cite which source you used.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""

    # Step 4: Call Claude API
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    answer = message.content[0].text
    
    print(f"\nQUESTION: {query}")
    print(f"\nANSWER: {answer}")
    print(f"\nSOURCES SEARCHED: {list(set(sources))}")
    
    return answer

if __name__ == "__main__":
    answer_question("What is model evaluation?")