import hashlib
from pathlib import Path

from sqlalchemy import select

from finguard.db.models import Document
from finguard.db.database import SessionLocal


def backfill_document_hashes():
    with SessionLocal() as session:
        documents = session.scalars(
            select(Document).where(Document.content_hash.is_(None))
        ).all()

        for document in documents:
            pdf_path = Path(document.source_path)

            if not pdf_path.is_file():
                print(f"File not found: {pdf_path}")
                continue

            content_hash = hashlib.sha256(
                pdf_path.read_bytes()
            ).hexdigest()

            existing = session.scalar(
                select(Document.id).where(
                    Document.content_hash == content_hash
                )
            )

            if existing is not None:
                print(
                    f"Hash already belongs to document {existing}; "
                    f"skipping document {document.id}"
                )
                continue

            document.content_hash = content_hash
            print(f"Updated document {document.id}: {document.filename}")

        session.commit()


if __name__ == "__main__":
    backfill_document_hashes()