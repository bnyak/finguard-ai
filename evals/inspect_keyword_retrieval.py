
from finguard.db.database import SessionLocal
from finguard.retrieval.keyword import retrieve_keyword_chunks


questions = [
    "What is a balloon payment in a mortgage?",
    "What is a mortgage rate lock?",
    "What is a HELOC?",
]

with SessionLocal() as session:
    for question in questions:
        results = retrieve_keyword_chunks(
            session=session,
            query=question,
            top_k=5,
            document_id=2,
        )

        print(f"\nQuestion: {question}")
        print(f"Retrieved IDs: {[chunk.id for chunk, _ in results]}")
        print(f"Scores: {[round(score, 4) for _, score in results]}")
