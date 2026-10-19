from pathlib import Path

from src.finguard.db.database import SessionLocal
from finguard.db.repositories import create_chunks, create_document
from finguard.embeddings.bge import embed_documents
from finguard.ingestion.chunker import chunk_pages
from finguard.ingestion.pdf_reader import extract_pages
from finguard.db.models import Document

import hashlib
from sqlalchemy import select


def ingest_pdf(
    pdf_path: Path,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> int:

    # 1. Calculate file fingerprint
    content_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()

    session = SessionLocal()

    try:
        # 2. Check whether this PDF already exists
        existing_document_id = session.scalar(
            select(Document.id).where(Document.content_hash == content_hash)
        )

        if existing_document_id is not None:
            return existing_document_id

        # 3. Process only new PDFs
        pages = extract_pages(pdf_path)

        chunks = chunk_pages(
            pages=pages,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        embeddings = embed_documents(
            [chunk["text"] for chunk in chunks]
        )

        # 4. Save document metadata
        document = create_document(
            session=session,
            filename=pdf_path.name,
            source_path=str(pdf_path),
            content_hash=content_hash,
        )

        # 5. Save chunks and embeddings
        create_chunks(
            session=session,
            document_id=document.id,
            chunks=chunks,
            embeddings=embeddings,
        )

        session.commit()

        return document.id

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()