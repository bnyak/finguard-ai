from unittest.mock import MagicMock, patch

from finguard.rag.service import answer_question


@patch("finguard.rag.service.generate_answer")
@patch("finguard.rag.service.retrieve_chunks")
@patch("finguard.rag.service.SessionLocal")
def test_answer_question_returns_answer_and_sources(
    mock_session_local,
    mock_retrieve_chunks,
    mock_generate_answer,
):
    session = MagicMock()
    mock_session_local.return_value = session

    document = MagicMock()
    document.filename = "sample_policy.pdf"

    chunk = MagicMock()
    chunk.document = document
    chunk.page_number = 2
    chunk.chunk_index = 0
    chunk.text = (
        "Enhanced review is required for high-risk customers "
        "and suspicious activity."
    )

    mock_retrieve_chunks.return_value = [
        (chunk, 0.2753)
    ]

    mock_generate_answer.return_value = (
        "Enhanced review is required for high-risk customers "
        "and suspicious activity."
    )

    result = answer_question(
        "When is enhanced review required?",
        top_k=1,
    )

    assert result.answer == (
        "Enhanced review is required for high-risk customers "
        "and suspicious activity."
    )

    assert len(result.sources) == 1
    assert result.sources[0]["filename"] == "sample_policy.pdf"
    assert result.sources[0]["page_number"] == 2
    assert result.sources[0]["chunk_index"] == 0
    assert result.sources[0]["distance"] == 0.2753

    session.close.assert_called_once()



def test_rag_abstains_when_no_chunks_are_retrieved():
    with (
        patch("finguard.rag.service.SessionLocal") as mock_session_local,
        patch(
            "finguard.rag.service.retrieve_chunks",
            return_value=[],
        ),
        patch("finguard.rag.service.generate_answer") as mock_generate,
    ):
        result = answer_question(
            "What is the company's confidential fraud threshold?"
        )

    assert result.answer == (
        "I don't have enough information in the provided documents."
    )
    assert result.sources == []
    mock_generate.assert_not_called()
    mock_session_local.return_value.close.assert_called_once()


def test_rag_rejects_irrelevant_retrieved_chunks():
    document = MagicMock()
    document.filename = "mortgage_guide.pdf"

    chunk = MagicMock()
    chunk.document = document
    chunk.page_number = 1
    chunk.chunk_index = 0
    chunk.text = "Mortgage points are upfront fees paid at closing."

    with (
        patch("finguard.rag.service.SessionLocal") as mock_session_local,
        patch(
            "finguard.rag.service.retrieve_chunks",
            return_value=[(chunk, 0.95)],
        ),
        patch("finguard.rag.service.generate_answer") as mock_generate,
    ):
        result = answer_question(
            "What is the company's fraud detection threshold?"
        )

    assert result.answer == (
        "I don't have enough information in the provided documents."
    )
    assert result.sources == []
    mock_generate.assert_not_called()
    mock_session_local.return_value.close.assert_called_once()



def test_rag_filters_irrelevant_chunks_but_keeps_relevant_ones():
    relevant = MagicMock()
    relevant.document.filename = "fraud_policy.pdf"
    relevant.page_number = 2
    relevant.chunk_index = 0
    relevant.text = "High-risk transactions require enhanced review."

    irrelevant = MagicMock()
    irrelevant.document.filename = "mortgage_guide.pdf"
    irrelevant.page_number = 5
    irrelevant.chunk_index = 1
    irrelevant.text = "Mortgage points are fees paid at closing."

    with (
        patch("finguard.rag.service.SessionLocal"),
        patch(
            "finguard.rag.service.retrieve_chunks",
            return_value=[
                (relevant, 0.25),
                (irrelevant, 0.95),
            ],
        ),
        patch(
            "finguard.rag.service.generate_answer",
            return_value="Enhanced review is required.",
        ) as mock_generate,
    ):
        result = answer_question(
            "When is enhanced review required?"
        )

    assert result.answer == "Enhanced review is required."
    assert len(result.sources) == 1
    assert result.sources[0]["filename"] == "fraud_policy.pdf"

    context = mock_generate.call_args.kwargs["context"]
    assert relevant.text in context
    assert irrelevant.text not in context
