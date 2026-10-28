from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000 )
    top_k: int = Field(default=3, ge=1, le=10)

class SourceResponse(BaseModel):
    filename: str
    page_number: int
    chunk_index: int
    text: str
    distance: float

class AskResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]


class AgentAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    max_steps: int = Field(default=5, ge=1, le=10)

class AgentAskResponse(BaseModel):
    answer : str
    tools_used: list[str]

class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    message: str