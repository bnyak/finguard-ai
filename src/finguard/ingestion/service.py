import hashlib
from pathlib import Path

from sqlalchemy import delete, select

from finguard.db.database import SessionLocal
from finguard.db.models import Document, DocumentChunk
from finguard.db.repositories import create_chunks, create_document
from finguard.embeddings.bge import embed_documents
from finguard.ingestion.chunker import chunk_pages
from finguard.ingestion.pdf_reader import extract_pages


def ingest_pdf(
    pdf_path: Path,
    chunk_size: int = 1000,
    overlap: int = 200,
    document_id: int | None = None,
) -> int:
    """Ingest a new PDF or replace an existing document."""

    content_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()

    session = SessionLocal()

    try:
        # Check whether this exact file already exists.
        existing_document_id = session.scalar(
            select(Document.id).where(Document.content_hash == content_hash ))

        # NEW DOCUMENT: skip duplicate files.
        if document_id is None:
            if existing_document_id is not None:
                return existing_document_id

            document = None

        # UPDATE: preserve the existing document ID.
        else:
            document = session.get(Document, document_id)

            if document is None:
                raise ValueError(f"Document {document_id} does not exist")

            # Same document, unchanged content.
            if existing_document_id == document_id:
                return document_id

            # The new file belongs to another document.
            if existing_document_id is not None:
                raise ValueError(
                    "This PDF already belongs to "
                    f"document {existing_document_id}"
                )

        # Process the replacement PDF.
        pages = extract_pages(pdf_path)

        chunks = chunk_pages(
            pages=pages,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        embeddings = embed_documents(
            [chunk["text"] for chunk in chunks]
        )

        if document_id is None:
            document = create_document(
                session=session,
                filename=pdf_path.name,
                source_path=str(pdf_path),
                content_hash=content_hash,
            )
        else:
            # Remove the previous document chunks.
            session.execute(
                delete(DocumentChunk).where(
                    DocumentChunk.document_id == document_id
                )
            )

            # Update metadata without changing the ID.
            document.filename = pdf_path.name
            document.source_path = str(pdf_path)
            document.content_hash = content_hash

        # Insert the new chunks and embeddings.
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
