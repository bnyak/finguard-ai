from unittest.mock import MagicMock, patch

import numpy as np

from finguard.embeddings.bge import embed_documents, embed_query


@patch("finguard.embeddings.bge.get_model")
def test_embed_documents_returns_embeddings(mock_get_model):
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array(
        [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ]
    )
    mock_get_model.return_value = mock_model

    result = embed_documents(["first chunk", "second chunk"])

    assert result == [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    mock_model.encode.assert_called_once_with(
        ["first chunk", "second chunk"],
        normalize_embeddings=True,
    )


@patch("finguard.embeddings.bge.get_model")
def test_embed_query_returns_embedding(mock_get_model):
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
    mock_get_model.return_value = mock_model

    result = embed_query("When is enhanced review required?")

    assert result == [0.1, 0.2, 0.3]


def test_embed_documents_empty_list():
    assert embed_documents([]) == []


def test_embed_query_rejects_empty_query():
    try:
        embed_query("   ")
        assert False, "Expected ValueError"
    except ValueError:
        pass