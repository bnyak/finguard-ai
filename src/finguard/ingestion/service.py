from pathlib import Path

from finguard.db.database import SessionLocal
from finguard.db.repositories import create_chunks, create_document
from finguard.ingestion.chunker import chunk_pages
from finguard.ingestion.pdf_reader import extract_pages


def ingest_pdf(
    pdf_path: Path,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> int:
    """Ingest a PDF document and persist its chunks."""

    pages = extract_pages(pdf_path)
    chunks = chunk_pages( pages=pages, chunk_size=chunk_size, overlap=overlap, )

    session = SessionLocal()

    try:
        document = create_document(
            session=session,
            filename=pdf_path.name,
            source_path=str(pdf_path),
        )

        create_chunks(
            session=session,
            document_id=document.id,
            chunks=chunks,
        )

        session.commit()

        return document.id

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()