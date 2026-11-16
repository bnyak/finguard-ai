
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from finguard.db.models import DocumentChunk


def retrieve_keyword_chunks(
    session: Session,
    query: str,
    top_k: int = 5,
    document_id: int | None = None,
) -> list[tuple[DocumentChunk, float]]:
    """Retrieve chunks using PostgreSQL full-text search."""

    search_vector = func.to_tsvector("english", DocumentChunk.text,)

    search_query = func.websearch_to_tsquery("english", query,)

    rank = func.ts_rank(search_vector, search_query)

    statement = (
        select(DocumentChunk, rank.label("rank"))
        .where(search_vector.op("@@")(search_query))
    )

    if document_id is not None:
        statement = statement.where(
            DocumentChunk.document_id == document_id
        )

    statement = (
        statement
        .order_by(rank.desc(), DocumentChunk.id)
        .limit(top_k)
    )

    results = session.execute(statement).all()

    return [
        (chunk, float(score))
        for chunk, score in results
    ]
