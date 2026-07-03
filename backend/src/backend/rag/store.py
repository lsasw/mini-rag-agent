import json
import math
import re
import uuid
from collections import Counter
from pathlib import Path
from typing import Any

from backend.config import get_settings
from backend.schemas import DocumentInfo, Source

TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+")


def _index_path() -> Path:
    return get_settings().data_dir / "index.json"


def _load_index() -> dict[str, Any]:
    path = _index_path()
    if not path.exists():
        return {"documents": {}, "chunks": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_index(index: dict[str, Any]) -> None:
    _index_path().write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def _vector(text: str) -> Counter[str]:
    return Counter(_tokens(text))


def _cosine(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    overlap = set(left) & set(right)
    dot = sum(left[token] * right[token] for token in overlap)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return dot / (left_norm * right_norm)


def add_document(filename: str, chunks: list[str]) -> DocumentInfo:
    index = _load_index()
    document_id = str(uuid.uuid4())
    characters = sum(len(chunk) for chunk in chunks)
    index["documents"][document_id] = {
        "id": document_id,
        "filename": filename,
        "chunks": len(chunks),
        "characters": characters,
    }
    for chunk_index, chunk in enumerate(chunks):
        index["chunks"].append(
            {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": chunk_index,
                "text": chunk,
            }
        )
    _save_index(index)
    return DocumentInfo(id=document_id, filename=filename, chunks=len(chunks), characters=characters)


def list_documents() -> list[DocumentInfo]:
    index = _load_index()
    return [DocumentInfo(**document) for document in index["documents"].values()]


def remove_document(document_id: str) -> bool:
    index = _load_index()
    if document_id not in index["documents"]:
        return False
    del index["documents"][document_id]
    index["chunks"] = [chunk for chunk in index["chunks"] if chunk["document_id"] != document_id]
    _save_index(index)
    return True


def search(query: str, limit: int = 4) -> list[tuple[Source, str]]:
    index = _load_index()
    query_vector = _vector(query)
    scored: list[tuple[float, dict[str, Any]]] = []
    for chunk in index["chunks"]:
        score = _cosine(query_vector, _vector(chunk["text"]))
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)

    results: list[tuple[Source, str]] = []
    for score, chunk in scored[:limit]:
        text = chunk["text"]
        results.append(
            (
                Source(
                    document_id=chunk["document_id"],
                    filename=chunk["filename"],
                    chunk_index=chunk["chunk_index"],
                    score=round(score, 4),
                    preview=text[:220],
                ),
                text,
            )
        )
    return results
