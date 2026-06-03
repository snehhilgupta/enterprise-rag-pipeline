# Enterprise RAG Pipeline

**A production-pattern Retrieval-Augmented Generation system for enterprise document intelligence.**

Built by [Snehhil Gupta](https://github.com/snehhilgupta) — Sr. TPM Applied AI transitioning to AI Architect.

---

## Problem Statement

Enterprise organizations sit on vast libraries of unstructured documents — leases, contracts, property reports, policy PDFs. Employees spend hours manually searching these documents for specific clauses, terms, and data points. Traditional keyword search fails because it matches words, not meaning.

This system solves that. Feed it any collection of enterprise documents and ask questions in plain English. It retrieves the most semantically relevant content and returns grounded, cited answers — with no hallucination.

**Target use case:** Commercial real estate firms managing thousands of lease agreements, property reports, and compliance documents. Maps directly to the "Chat with Data" strategy I architected at CBRE.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      RAG PIPELINE                           │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────┐  │
│  │  ingest  │───▶│  embed   │───▶│      ChromaDB        │  │
│  │  .py     │    │  .py     │    │   (Vector Store)     │  │
│  └──────────┘    └──────────┘    └──────────────────────┘  │
│  Load PDFs       Convert to             │                   │
│  Chunk text      vectors                │ semantic search   │
│                                         ▼                   │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────┐  │
│  │ answer   │◀───│ retrieve │◀───│    User Question     │  │
│  │ .py      │    │ .py      │    └──────────────────────┘  │
│  └──────────┘    └──────────┘                              │
│  Claude API      Top-K chunks                              │
│  Grounded answer with citations                            │
└─────────────────────────────────────────────────────────────┘
```

**Flow:**
1. Documents are loaded, chunked, and embedded into ChromaDB at index time
2. At query time, the user's question is embedded using the same model
3. ChromaDB returns the top-K chunks with highest semantic similarity
4. Those chunks are passed to Claude with a grounding prompt
5. Claude answers using only the provided context — never its training data

---

## Stack

| Component | Technology | Reason |
|-----------|-----------|--------|
| Framework | LangChain | Industry-standard LLM orchestration |
| Vector DB | ChromaDB | Open-source, local, zero infrastructure cost |
| Embedding Model | ChromaDB MiniLM (local) | Runs on-device, no API cost, no data egress |
| LLM | Anthropic Claude | Best-in-class instruction following and grounding |
| Document Loader | PyPDF via LangChain | Handles enterprise PDF formats |

---

## Key Design Decisions

### 1. Chunk Size: 500 tokens with 50-token overlap
The LLM has a fixed context window — it cannot process an entire document at once. 500 tokens is large enough to contain a complete idea or clause, small enough to keep retrieval precise. The 50-token overlap prevents context loss at chunk boundaries — a lease clause split across two chunks won't lose its meaning.

**Tradeoff:** Smaller chunks improve retrieval precision but lose surrounding context. Larger chunks preserve context but reduce retrieval accuracy. 500/50 is a proven starting point for enterprise documents.

### 2. Vector Database over Knowledge Graph
ChromaDB stores document chunks as vectors and retrieves by semantic similarity. A knowledge graph would store entities and relationships (Tenant → leases → Property → located in → City).

**Decision:** Vector database. Our documents are unstructured PDFs where meaning matters more than relationships. Semantic similarity search outperforms relationship traversal for this use case. A hybrid approach (vector + graph) would be the production evolution.

### 3. Local Embeddings over API Embeddings
Using ChromaDB's built-in MiniLM model instead of OpenAI embeddings. This means embeddings run entirely on-device — no API cost, no data leaving the machine, no latency on embedding calls.

**Tradeoff:** Slightly lower embedding quality than OpenAI's text-embedding-3-large, but more than sufficient for document retrieval. In a production system with sensitive enterprise data, local embeddings are often a compliance requirement.

### 4. Grounding Prompt Design
The prompt explicitly instructs Claude to answer only from provided context and say "I don't have enough information" when the answer isn't present. This is the primary hallucination prevention mechanism.

**Why this matters:** In enterprise settings, a wrong answer cited confidently is worse than no answer. The system is designed to be honest about its limits.

### 5. Top-K = 5
Passing 5 chunks to Claude balances context richness against context window usage and cost. Too few chunks risk missing the answer. Too many chunks dilute relevance and increase API cost.

---

## What Works Well

- Semantic search correctly identifies relevant content even when the question uses different words than the document
- Grounding prompt reliably prevents Claude from hallucinating beyond the provided context
- Local embeddings mean zero API cost and zero data egress during indexing
- Source citations in every answer make responses auditable

---

## Known Limitations

| Limitation | Production Fix |
|-----------|---------------|
| No re-ranking of retrieved chunks | Add a cross-encoder re-ranker (e.g. Cohere Rerank) for higher precision |
| Single vector store, no multi-tenancy | Partition ChromaDB collections by client or document type |
| No conversation memory | Add LangChain ConversationBufferMemory for multi-turn Q&A |
| Local ChromaDB doesn't scale | Migrate to Pinecone or Weaviate for distributed, production-scale retrieval |
| PDF parsing loses table structure | Add a specialized table parser (e.g. Camelot) for structured data extraction |
| API keys in .env file | Replace with AWS Secrets Manager or Azure Key Vault in production |

---

## What's Next

**Short term:**
- Add a simple CLI interface for interactive Q&A sessions
- Expand test suite to 50 queries across document types

**Production evolution:**
- Hybrid retrieval: combine vector similarity with BM25 keyword search for higher recall
- Agentic layer: wrap this pipeline as a tool inside a LangGraph multi-agent system (see Project 2)
- Evaluation framework: add RAGAS for automated RAG quality scoring
- Streaming responses: stream Claude's answer token-by-token for better UX

---

## Project Structure

```
enterprise-rag-pipeline/
├── data/                  # Source documents (PDFs)
├── src/
│   ├── ingest.py          # Load + chunk documents
│   ├── embed.py           # Embed chunks into ChromaDB
│   ├── retrieve.py        # Semantic search against vector store
│   └── answer.py          # Grounded answer generation via Claude API
├── main.py                # Entry point
├── .env                   # API keys (never committed)
├── requirements.txt       # Pinned dependencies
└── README.md              # This document
```

## Usage

**Index your documents:**
```bash
python main.py
```

**Ask a question:**
```bash
python main.py "What are the termination clauses in the lease agreements?"
```

---

## Author

**Snehhil Gupta** — Sr. TPM Applied AI at CBRE, transitioning to AI Architect / Director of AI Programs.

This project is part of a portfolio demonstrating hands-on AI system design and implementation capability — not just program management.

[GitHub](https://github.com/snehhilgupta)