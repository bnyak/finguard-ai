# ADR-002: Vector Storage

## Status

Accepted

## Decision

FinGuard AI will use PostgreSQL with the pgvector extension as its primary vector and relational data store.

## Context

The platform will need to store and retrieve:

- document metadata
- document chunks
- embeddings
- structured financial data
- investigation-related data

The system will eventually require semantic retrieval, metadata filtering, SQL queries, and hybrid retrieval.

## Decision Rationale

PostgreSQL with pgvector allows FinGuard AI to combine relational data and vector embeddings in the same database.

This provides:

- SQL support
- vector similarity search
- metadata filtering
- relational constraints
- transactional consistency
- PostgreSQL full-text search
- support for hybrid retrieval architectures

Using PostgreSQL also avoids introducing a separate vector database during the initial architecture.

## Consequences

- PostgreSQL will be required for local and production environments.
- pgvector will be used for embedding storage and similarity search.
- Vector indexes such as HNSW can be introduced as the dataset grows.
- Hybrid retrieval can later combine semantic vector search with lexical search.
- A dedicated vector database can still be evaluated later if scale or retrieval requirements justify it.