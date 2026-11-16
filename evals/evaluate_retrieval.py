
import json
from pathlib import Path

from finguard.db.database import SessionLocal
from finguard.retrieval.semantic import retrieve_chunks
from finguard.retrieval.keyword import retrieve_keyword_chunks
from finguard.evaluation.retrieval_metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


RETRIEVAL_METHOD = "keyword"
EVAL_DIR = Path(__file__).resolve().parent
DATASET_PATH = EVAL_DIR / "datasets" / "retrieval_questions.json"
RESULTS_PATH = EVAL_DIR / "results" / f"{RETRIEVAL_METHOD}_baseline.json"
TOP_K = 5


def main():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    if not questions:
        print("No evaluation questions found.")
        return

    evaluation_results = []

    with SessionLocal() as session:
        for item in questions:
            question = item["question"]
            relevant_ids = set(item["relevant_chunk_ids"])

            if RETRIEVAL_METHOD == "dense":
                results = retrieve_chunks(
                    session=session,
                    query=question,
                    top_k=TOP_K,
                    document_id=2,
                )

            elif RETRIEVAL_METHOD == "keyword":
                results = retrieve_keyword_chunks(
                    session=session,
                    query=question,
                    top_k=TOP_K,
                    document_id=2,
                )

            else:
                raise ValueError(
                    f"Unsupported retrieval method: {RETRIEVAL_METHOD}"
                )

            retrieved_ids = [
                chunk.id for chunk, distance in results
            ]
            found_relevant_ids = [
                chunk_id
                for chunk_id in retrieved_ids
                if chunk_id in relevant_ids
            ]

            missing_relevant_ids = sorted(
                relevant_ids - set(retrieved_ids)
            )
            precision = precision_at_k(
                retrieved_ids, relevant_ids, TOP_K
            )
            recall = recall_at_k(
                retrieved_ids, relevant_ids, TOP_K
            )
            rr = reciprocal_rank(
                retrieved_ids, relevant_ids
            )

            evaluation_results.append({
                "question_id": item["question_id"],
                "question": question,
                "document_id": item["document_id"],
                "category": item["category"],
                "relevant_chunk_ids": sorted(relevant_ids),
                "retrieved_chunk_ids": retrieved_ids,
                "found_relevant_ids": found_relevant_ids,
                "missing_relevant_ids": missing_relevant_ids,
                "precision_at_5": precision,
                "recall_at_5": recall,
                "reciprocal_rank": rr,
                "retrieval_method": RETRIEVAL_METHOD,
            })

            print(f"\nQuestion: {item['question_id']}")
            print(f"Retrieved: {retrieved_ids}")
            print(f"Relevant: {relevant_ids}")
            print(f"Found_relevant_ids: {found_relevant_ids}")
            print(f"missing_relevant_ids: {missing_relevant_ids}")
            print(f"Precision@5: {precision:.4f}")
            print(f"Recall@5: {recall:.4f}")
            print(f"Reciprocal Rank: {rr:.4f}")
            print(f"retrieval_method: {RETRIEVAL_METHOD}")

    total = len(evaluation_results)

    mean_precision = sum(
        item["precision_at_5"] for item in evaluation_results
    ) / total

    mean_recall = sum(
        item["recall_at_5"] for item in evaluation_results
    ) / total

    mrr = sum(
        item["reciprocal_rank"] for item in evaluation_results
    ) / total

    report = {
        "retrieval_method": RETRIEVAL_METHOD,
        "embedding_model": ("bge-small-en-v1.5" if RETRIEVAL_METHOD == "dense"  else None),
        "top_k": TOP_K,
        "total_questions": total,
        "ground_truth_status": "provisional",
        "mean_precision_at_5": mean_precision,
        "mean_recall_at_5": mean_recall,
        "mrr": mrr,
        "per_question": evaluation_results,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with RESULTS_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("\n" + "=" * 50)
    print(f"Total questions: {total}")
    print(f"Mean Precision@5: {mean_precision:.4f}")
    print(f"Mean Recall@5: {mean_recall:.4f}")
    print(f"MRR: {mrr:.4f}")
    print(f"\nResults saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
