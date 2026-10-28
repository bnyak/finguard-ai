
from langchain_core.tools import tool

from finguard.db.database import SessionLocal
from finguard.retrieval.semantic import retrieve_chunks


@tool
def search_documents(query: str, top_k: int = 3,document_id: int | None = None,) -> str:
    """Search uploaded financial documents using semantic similarity.

    Use this tool when the user asks about information contained
    in uploaded PDFs, including mortgage policies and CFPB guidance.
    """
    with SessionLocal() as session:
        results = retrieve_chunks(
            session=session,
            query=query,
            top_k = max(3, min(top_k, 5)),
            document_id=document_id,
        )

        if not results:
            return "No relevant document passages were found."

        passages = []

        for chunk, distance in results:
            passages.append(
                f"Document ID: {chunk.document_id}\n"
                f"Page: {chunk.page_number}\n"
                f"Chunk: {chunk.chunk_index}\n"
                f"Content: {chunk.text}\n"
                f"Cosine distance: {distance:.4f}"
            )

        return "\n\n---\n\n".join(passages)
