from pathlib import Path
from unittest.mock import MagicMock, patch

from finguard.ingestion.service import ingest_pdf


def test_duplicate_pdf_skips_processing(tmp_path: Path):
    pdf_path = tmp_path / "policy.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\nsample content")

    mock_session = MagicMock()
    mock_session.scalar.return_value = 42

    with (
        patch(
            "finguard.ingestion.service.SessionLocal",
            return_value=mock_session,
        ),
        patch("finguard.ingestion.service.extract_pages") as mock_extract,
        patch("finguard.ingestion.service.embed_documents") as mock_embed,
    ):
        document_id = ingest_pdf(pdf_path)

    assert document_id == 42
    mock_session.scalar.assert_called_once()
    mock_extract.assert_not_called()
    mock_embed.assert_not_called()
    mock_session.close.assert_called_once()


def test_update_document_preserves_document_id(tmp_path: Path):
    pdf_path = tmp_path / "policy_updated.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\nupdated policy content")

    mock_session = MagicMock()

    # No document has the new PDF's content hash.
    mock_session.scalar.return_value = None

    # Document 42 already exists.
    existing_document = MagicMock()
    existing_document.id = 42
    mock_session.get.return_value = existing_document

    chunks = [
        {
            "page_number": 1,
            "chunk_index": 0,
            "text": "Updated policy content",
        }
    ]
    embeddings = [[0.1] * 384]

    with (
        patch(
            "finguard.ingestion.service.SessionLocal",
            return_value=mock_session,
        ),
        patch(
            "finguard.ingestion.service.extract_pages",
            return_value=[(1, "Updated policy content")],
        ),
        patch(
            "finguard.ingestion.service.chunk_pages",
            return_value=chunks,
        ),
        patch(
            "finguard.ingestion.service.embed_documents",
            return_value=embeddings,
        ),
        patch(
            "finguard.ingestion.service.create_chunks"
        ) as mock_create_chunks,
    ):
        document_id = ingest_pdf(
            pdf_path,
            document_id=42,
        )

    assert document_id == 42

    # Existing document metadata was updated.
    assert existing_document.filename == "policy_updated.pdf"

    # Old chunks were scheduled for deletion.
    mock_session.execute.assert_called_once()

    # New chunks were created for the same document.
    mock_create_chunks.assert_called_once()
    assert mock_create_chunks.call_args.kwargs["document_id"] == 42

    # Database transaction was committed.
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()

import pytest


def test_update_rolls_back_when_chunk_creation_fails(tmp_path: Path):
    pdf_path = tmp_path / "policy_updated.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\nupdated policy content")

    mock_session = MagicMock()
    mock_session.scalar.return_value = None

    existing_document = MagicMock()
    existing_document.id = 42
    mock_session.get.return_value = existing_document

    chunks = [
        {
            "page_number": 1,
            "chunk_index": 0,
            "text": "Updated policy content",
        }
    ]

    with (
        patch(
            "finguard.ingestion.service.SessionLocal",
            return_value=mock_session,
        ),
        patch(
            "finguard.ingestion.service.extract_pages",
            return_value=[(1, "Updated policy content")],
        ),
        patch(
            "finguard.ingestion.service.chunk_pages",
            return_value=chunks,
        ),
        patch(
            "finguard.ingestion.service.embed_documents",
            return_value=[[0.1] * 384],
        ),
        patch(
            "finguard.ingestion.service.create_chunks",
            side_effect=RuntimeError("Database insert failed"),
        ),
    ):
        with pytest.raises(RuntimeError, match="Database insert failed"):
            ingest_pdf(pdf_path, document_id=42)

    mock_session.execute.assert_called_once()
    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()
    mock_session.close.assert_called_once()

def test_update_rejects_content_owned_by_another_document(
    tmp_path: Path,
):
    pdf_path = tmp_path / "duplicate.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\nexisting content")

    mock_session = MagicMock()

    # The uploaded content already belongs to document 57.
    mock_session.scalar.return_value = 57

    # The document we want to update is document 42.
    existing_document = MagicMock()
    existing_document.id = 42
    mock_session.get.return_value = existing_document

    with (
        patch(
            "finguard.ingestion.service.SessionLocal",
            return_value=mock_session,
        ),
        patch(
            "finguard.ingestion.service.extract_pages",
        ) as mock_extract,
    ):
        with pytest.raises(
            ValueError,
            match="This PDF already belongs to document 57",
        ):
            ingest_pdf(pdf_path, document_id=42)

    # The PDF must not be processed.
    mock_extract.assert_not_called()

    # No document chunks should be deleted.
    mock_session.execute.assert_not_called()

    # No changes should be committed.
    mock_session.commit.assert_not_called()

    # Session must be cleaned up.
    mock_session.close.assert_called_once()
