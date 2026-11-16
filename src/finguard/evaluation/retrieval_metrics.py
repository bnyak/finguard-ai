
def recall_at_k(
    retrieved_ids: list[int],
    relevant_ids: set[int],
    k: int,
) -> float:
    """Fraction of relevant chunks found in the top k."""

    if k <= 0:
        raise ValueError("k must be positive")

    if not relevant_ids:
        raise ValueError("Relevant IDs cannot be empty")

    top_k = set(retrieved_ids[:k])

    matches = top_k.intersection(relevant_ids)

    return len(matches) / len(relevant_ids)


def reciprocal_rank(
    retrieved_ids: list[int],
    relevant_ids: set[int],
) -> float:
    """Reciprocal rank of the first relevant chunk."""

    for rank, chunk_id in enumerate(
        retrieved_ids, start=1
    ):
        if chunk_id in relevant_ids:
            return 1.0 / rank

    return 0.0

def precision_at_k(
    retrieved_ids: list[int],
    relevant_ids: set[int],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError("k must be positive")

    top_k = retrieved_ids[:k]
    matches = sum(
        1 for chunk_id in top_k
        if chunk_id in relevant_ids
    )

    return matches / k