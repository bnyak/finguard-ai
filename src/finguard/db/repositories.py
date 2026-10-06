from sqlalchemy.orm import Session

from finguard.db.models import Document, DocumentChunk


def create_document(
    session: Session,
    filename: str,
    source_path: str | None = None,
) -> Document:
    """Create and persist a document record."""

    document = Document(
        filename=filename,
        source_path=source_path,
    )

    session.add(document)
    session.flush()

    return document

def create_chunks(
    session: Session,
    document_id: int,
    chunks: list[dict],
) -> list[DocumentChunk]:
    """Create and persist document chunk records."""

    chunk_records = []

    for chunk in chunks:
        chunk_record = DocumentChunk(
            document_id=document_id,
            page_number=chunk["page_number"],
            chunk_index=chunk["chunk_index"],
            text=chunk["text"],
        )

        chunk_records.append(chunk_record)

    session.add_all(chunk_records)
    session.flush()

    return chunk_records