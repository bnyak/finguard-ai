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