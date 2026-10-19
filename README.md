# FinGuard AI

FinGuard AI is a financial document intelligence platform for building and evaluating production-style Retrieval-Augmented Generation (RAG) workflows.

The project currently implements an end-to-end RAG pipeline for financial policy documents, combining local embeddings, PostgreSQL/pgvector semantic search, grounded LLM generation, and document-level provenance.

## Project Status

Under active development.

### Current V1 Capabilities

- PDF ingestion with page-level metadata
- Overlapping document chunking with provenance preservation
- Local document and query embeddings using BAAI/bge-small-en-v1.5
- PostgreSQL persistence with pgvector vector storage
- Database schema management with SQLAlchemy and Alembic
- Semantic retrieval using cosine distance
- Grounded question answering using a local Qwen3 model through Ollama
- Document filename, page, and chunk provenance for retrieved evidence
- Abstention when retrieved context does not contain sufficient information
- Automated unit tests for ingestion, chunking, embeddings, and RAG orchestration

## Current RAG Architecture

```text
Financial PDF
     |
     v
PDF Extraction
     |
     v
Page-Aware Chunking
     |
     v
BGE Embeddings
     |
     v
PostgreSQL + pgvector
     |
     v
Semantic Retrieval
     |
     v
Retrieved Evidence
     |
     v
Ollama / Qwen3
     |
     v
Grounded Answer + Sources