from fastapi import APIRouter, HTTPException

from backend.llama.crud import llama_store
from backend.schemas import (
    LlamaDocument,
    LlamaDocumentCreate,
    LlamaDocumentUpdate,
    LlamaSearchRequest,
    LlamaSearchResponse,
)

router = APIRouter(prefix="/llama", tags=["llamaindex"])


@router.get("/categories", response_model=list[str])
def categories() -> list[str]:
    return llama_store.list_categories()


@router.get("/documents", response_model=list[LlamaDocument])
def documents(category: str | None = None) -> list[LlamaDocument]:
    return llama_store.list_documents(category)


@router.post("/documents", response_model=LlamaDocument)
def create_document(payload: LlamaDocumentCreate) -> LlamaDocument:
    return llama_store.create_document(payload)


@router.put("/documents/{document_id}", response_model=LlamaDocument)
def update_document(document_id: str, payload: LlamaDocumentUpdate) -> LlamaDocument:
    document = llama_store.update_document(document_id, payload)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/documents/{document_id}")
def delete_document(document_id: str) -> dict[str, bool]:
    deleted = llama_store.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True}


@router.post("/search", response_model=LlamaSearchResponse)
def search(payload: LlamaSearchRequest) -> LlamaSearchResponse:
    return llama_store.search(payload)
