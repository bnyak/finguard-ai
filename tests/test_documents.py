from unittest.mock import patch

from fastapi.testclient import TestClient

from finguard.api.main import app

client = TestClient(app)


def test_upload_valid_pdf():
    fake_pdf = b"%PDF-1.4\nfake PDF content"

    with patch(
        "finguard.api.routes.documents.ingest_pdf",
        return_value=3,
    ) as mock_ingest:

        response = client.post(
            "/documents",
            files={
                "file": ("test.pdf", fake_pdf, "application/pdf")
            },
        )

    assert response.status_code == 200
    assert response.json()["document_id"] == 3
    assert response.json()["filename"] == "test.pdf"
    mock_ingest.assert_called_once()


def test_upload_rejects_non_pdf():
    response = client.post(
        "/documents",
        files={
            "file": ("notes.txt", b"hello", "text/plain")
        },
    )

    assert response.status_code == 400


def test_upload_rejects_oversized_pdf():
    oversized_pdf = b"%PDF-" + b"x" * (10 * 1024 * 1024)

    response = client.post(
        "/documents",
        files={
            "file": ("large.pdf", oversized_pdf, "application/pdf")
        },
    )

    assert response.status_code == 413


def test_upload_rejects_invalid_pdf_signature():
    response = client.post(
        "/documents",
        files={
            "file": ("invalid.pdf", b"not a PDF", "application/pdf")
        },
    )

    assert response.status_code == 400