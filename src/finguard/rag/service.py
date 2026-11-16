from dataclasses import dataclass

from finguard.db.database import SessionLocal
from finguard.generation.ollama import generate_answer
from finguard.retrieval.semantic import retrieve_chunks

MAX_COSINE_DISTANCE = 0.70

@dataclass
class RAGResult:
    answer: str
    sources: list[dict]

def answer_question(question: str,top_k: int = 3,) -> RAGResult:
    """Answer a question using retrieved FinGuard document evidence."""

    session = SessionLocal()

    try:
        retrieved = retrieve_chunks(session=session, query=question, top_k=top_k, )

        relevant_chunks = [(chunk, distance) for chunk, distance in retrieved
                     if distance is not None and float(distance) <= MAX_COSINE_DISTANCE ]

        if not relevant_chunks:
            return RAGResult(
                answer=(
                    "I don't have enough information "
                    "in the provided documents."
                ),
                sources=[],
            )

        context_parts = []
        sources = []

        for chunk, distance in relevant_chunks:
            context_parts.append( f"[Page {chunk.page_number}]\n{chunk.text}"  )

            sources.append(
                {
                    "filename": chunk.document.filename,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                    "distance": float(distance),
                }
            )

        context = "\n\n".join(context_parts)
        answer = generate_answer(question=question, context=context, )

        return RAGResult( answer=answer,  sources=sources,  )

    finally:
        session.close()


