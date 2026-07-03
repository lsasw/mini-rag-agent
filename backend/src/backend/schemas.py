from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    use_agent: bool = False


class Source(BaseModel):
    document_id: str
    filename: str
    chunk_index: int
    score: float
    preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = []
    mode: str


class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunks: int
    characters: int


class UploadResponse(BaseModel):
    document: DocumentInfo
    message: str


class LlamaDocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=60)
    content: str = Field(min_length=1)


class LlamaDocumentUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=60)
    content: str = Field(min_length=1)


class LlamaDocument(BaseModel):
    id: str
    title: str
    category: str
    content: str


class LlamaSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    category: str | None = None
    top_k: int = Field(default=3, ge=1, le=10)


class LlamaSearchHit(BaseModel):
    document_id: str
    title: str
    category: str
    score: float | None
    preview: str


class LlamaSearchResponse(BaseModel):
    hits: list[LlamaSearchHit]
    note: str
