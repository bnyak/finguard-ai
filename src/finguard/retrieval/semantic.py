from sqlalchemy import select
from sqlalchemy.orm import Session

from finguard.db.models import DocumentChunk
from finguard.embeddings.bge import embed_query

def retrieve_chunks(
    session: Session,
    query: str,
    top_k: int = 5,
) -> list[tuple[DocumentChunk, float]]:
    """Retrieve document chunks most relevant to a query."""

    query_embedding = embed_query(query)

    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    statement = (
        select(DocumentChunk, distance.label("distance"))
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(top_k)
    )

    results = session.execute(statement).all()

    return [(row[0], row[1]) for row in results]