# FinGuard AI

FinGuard AI is an agentic financial intelligence and investigation platform built to explore production-grade Retrieval-Augmented Generation (RAG), structured data retrieval, and AI-assisted financial investigations.

## Project Status

🚧 Under active development.

## V1 Goal

Build a grounded financial document question-answering system that:

- ingests financial policy and regulatory documents
- extracts and chunks document content
- generates embeddings
- stores document chunks and embeddings in PostgreSQL with pgvector
- retrieves relevant evidence for user questions
- generates answers grounded in retrieved evidence
- returns source citations
- avoids unsupported answers when sufficient evidence is unavailable

## Planned Technology Stack

- Python 3.13
- FastAPI
- Pydantic
- PostgreSQL
- pgvector
- SQLAlchemy
- Alembic
- OpenAI API
- pytest

Additional production, agentic, cloud, and observability capabilities will be introduced incrementally.