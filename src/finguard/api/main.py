from fastapi import FastAPI

from finguard.api.schemas import AskRequest, AskResponse
from finguard.rag.service import answer_question

from finguard.api.routes.documents import router as documents_router

app = FastAPI(
    title="FinGuard AI",
    description="Financial Document Intelligence API",
    version="0.1.0",
)
app.include_router(documents_router)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):

    result = answer_question( question=request.question, top_k=request.top_k, )
    return AskResponse( answer=result.answer, sources=result.sources, )