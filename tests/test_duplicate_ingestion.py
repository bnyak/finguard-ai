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