import sys

from sqlalchemy import select

from finguard.db.models import DocumentChunk
from finguard.db.database import SessionLocal

sys.stdout.reconfigure(encoding="utf-8")


def main():
    with SessionLocal() as session:
        from sqlalchemy import func, select

        with SessionLocal() as session:
            statement = (
                select(DocumentChunk)
                .where(DocumentChunk.document_id == 2)
                .order_by(
                    DocumentChunk.page_number,
                    DocumentChunk.chunk_index,
                )
            )

        chunks = session.scalars(statement).all()

        for chunk in chunks:
            print("=" * 70)
            print(f"Chunk ID: {chunk.id}")
            print(f"Document ID: {chunk.document_id}")
            print(f"Page: {chunk.page_number}")
            print(f"Chunk index: {chunk.chunk_index}")
            print(f"Text: {chunk.text}")
            print()


if __name__ == "__main__":
    main()
