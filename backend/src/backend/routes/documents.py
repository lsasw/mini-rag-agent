from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.rag.ingest import ingest_upload
from backend.rag.store import list_documents, remove_document
from backend.schemas import DocumentInfo, UploadResponse

router = APIRouter(tags=["documents"])


@router.get("/documents", response_model=list[DocumentInfo])
def get_documents() -> list[DocumentInfo]:
    return list_documents()


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    if not file.filename.lower().endswith((".txt", ".md", ".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt, .md and .pdf files are supported")

    document = await ingest_upload(file)
    return UploadResponse(document=document, message="Document uploaded and indexed")


@router.delete("/documents/{document_id}")
def delete_document(document_id: str) -> dict[str, bool]:
    deleted = remove_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True}
