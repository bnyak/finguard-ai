from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIMENSION = 384

global _model
_model: SentenceTransformer | None = None



def get_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it."""
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model

def embed_documents(texts: list[str]) -> list[list[float]]:
    """Generate normalized embeddings for document chunks."""
    if not texts:
        return []

    model = get_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    return embeddings.tolist()


def embed_query(text: str) -> list[float]:
    """Generate a normalized embedding for a retrieval query."""
    if not text.strip():
        raise ValueError("Query text cannot be empty")

    model = get_model()

    query_text = (
        "Represent this sentence for searching relevant passages: "
        + text
    )

    embedding = model.encode(
        query_text,
        normalize_embeddings=True,
    )

    return embedding.tolist()