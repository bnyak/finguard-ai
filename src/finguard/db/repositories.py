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
    embeddings: list[list[float]],
) -> list[DocumentChunk]:
    if len(chunks) != len(embeddings):
        raise ValueError("Each chunk must have exactly one embedding")

    chunk_records = []

    for chunk, embedding in zip(chunks, embeddings):
        chunk_record = DocumentChunk(
            document_id=document_id,
            page_number=chunk["page_number"],
            chunk_index=chunk["chunk_index"],
            text=chunk["text"],
            embedding=embedding,
        )
        chunk_records.append(chunk_record)

    session.add_all(chunk_records)
    session.flush()

    return chunk_records