from fastapi.testclient import TestClient

from finguard.api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_rejects_empty_question():
    response = client.post(
        "/ask",
        json={"question": "", "top_k": 3},
    )

    assert response.status_code == 422


def test_ask_rejects_invalid_top_k():
    response = client.post(
        "/ask",
        json={"question": "What are mortgage points?", "top_k": 20},
    )

    assert response.status_code == 422

from unittest.mock import patch

from finguard.rag.service import RAGResult


def test_ask_success():
    fake_result = RAGResult(
        answer="Mortgage points can reduce the interest rate.",
        sources=[
            {
                "filename": "cfpb_your-home-loan-toolkit.pdf",
                "page_number": 10,
                "chunk_index": 0,
                "text": "Points are a percentage of a loan amount.",
                "distance": 0.25,
            }
        ],
    )

    with patch(
        "finguard.api.main.answer_question",
        return_value=fake_result,
    ) as mock_rag:

        response = client.post(
            "/ask",
            json={
                "question": "What are mortgage points?",
                "top_k": 3,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == fake_result.answer
    assert data["sources"][0]["page_number"] == 10

    mock_rag.assert_called_once_with(
        question="What are mortgage points?",
        top_k=3,
    )