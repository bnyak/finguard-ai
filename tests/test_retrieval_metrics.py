
import pytest

from finguard.evaluation.retrieval_metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_recall_at_3():
    retrieved = [10, 20, 30, 40]
    relevant = {20, 40}

    result = recall_at_k(retrieved, relevant, k=3)

    assert result == pytest.approx(0.5)


def test_reciprocal_rank():
    retrieved = [10, 20, 30]
    relevant = {30}

    result = reciprocal_rank(retrieved, relevant)

    assert result == pytest.approx(1 / 3)


def test_no_relevant_chunk_retrieved():
    retrieved = [10, 20, 30]
    relevant = {40}

    assert reciprocal_rank(retrieved, relevant) == 0.0


def test_precision_at_5():
    retrieved = [18, 17, 27, 19, 26]
    relevant = {17, 18, 19}

    assert precision_at_k(
        retrieved,
        relevant,
        k=5,
    ) == pytest.approx(0.6)
