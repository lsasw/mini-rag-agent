from pathlib import Path

from fastapi import UploadFile

from backend.config import get_settings
from backend.rag.loader import load_text
from backend.rag.splitter import split_text
from backend.rag.store import add_document
from backend.schemas import DocumentInfo


async def ingest_upload(file: UploadFile) -> DocumentInfo:
    settings = get_settings()
    safe_name = Path(file.filename or "upload.txt").name
    target = settings.data_dir / "uploads" / safe_name
    target.write_bytes(await file.read())

    text = load_text(target)
    chunks = split_text(text)
    return add_document(safe_name, chunks)
