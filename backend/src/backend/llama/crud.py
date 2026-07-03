import json
import uuid
from pathlib import Path

from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.embeddings import MockEmbedding

from backend.config import get_settings
from backend.schemas import (
    LlamaDocument,
    LlamaDocumentCreate,
    LlamaDocumentUpdate,
    LlamaSearchHit,
    LlamaSearchRequest,
    LlamaSearchResponse,
)

Settings.llm = None
Settings.embed_model = MockEmbedding(embed_dim=64)


class LlamaCrudStore:
    def __init__(self) -> None:
        self._index: VectorStoreIndex | None = None

    @property
    def data_path(self) -> Path:
        path = get_settings().data_dir / "llama_documents.json"
        if not path.exists():
            path.write_text("[]", encoding="utf-8")
        return path

    def _read(self) -> list[LlamaDocument]:
        raw = json.loads(self.data_path.read_text(encoding="utf-8"))
        return [LlamaDocument(**item) for item in raw]

    def _write(self, documents: list[LlamaDocument]) -> None:
        self.data_path.write_text(
            json.dumps([document.model_dump() for document in documents], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _to_llama_doc(self, document: LlamaDocument) -> Document:
        return Document(
            text=document.content,
            id_=document.id,
            metadata={"title": document.title, "category": document.category},
        )

    def _ensure_index(self) -> VectorStoreIndex:
        if self._index is None:
            llama_documents = [self._to_llama_doc(document) for document in self._read()]
            self._index = VectorStoreIndex.from_documents(llama_documents)
        return self._index

    def list_categories(self) -> list[str]:
        return sorted({document.category for document in self._read()})

    def list_documents(self, category: str | None = None) -> list[LlamaDocument]:
        documents = self._read()
        if category:
            return [document for document in documents if document.category == category]
        return documents

    def create_document(self, payload: LlamaDocumentCreate) -> LlamaDocument:
        document = LlamaDocument(
            id=str(uuid.uuid4()),
            title=payload.title,
            category=payload.category,
            content=payload.content,
        )
        documents = self._read()
        documents.append(document)
        self._write(documents)

        # LlamaIndex create: insert a new Document into an existing index.
        self._ensure_index().insert(self._to_llama_doc(document))
        return document

    def update_document(self, document_id: str, payload: LlamaDocumentUpdate) -> LlamaDocument | None:
        documents = self._read()
        updated: LlamaDocument | None = None
        next_documents: list[LlamaDocument] = []
        for document in documents:
            if document.id == document_id:
                updated = LlamaDocument(
                    id=document_id,
                    title=payload.title,
                    category=payload.category,
                    content=payload.content,
                )
                next_documents.append(updated)
            else:
                next_documents.append(document)

        if updated is None:
            return None

        self._write(next_documents)

        # LlamaIndex update: update_ref_doc deletes old nodes for id_ and inserts new nodes.
        self._ensure_index().update_ref_doc(self._to_llama_doc(updated))
        return updated

    def delete_document(self, document_id: str) -> bool:
        documents = self._read()
        if not any(document.id == document_id for document in documents):
            return False

        self._write([document for document in documents if document.id != document_id])

        # LlamaIndex delete: remove all nodes for the document id from the index/docstore.
        self._ensure_index().delete_ref_doc(document_id, delete_from_docstore=True)
        return True

    def search(self, payload: LlamaSearchRequest) -> LlamaSearchResponse:
        index = self._ensure_index()
        hits: list[LlamaSearchHit] = []
        retriever = index.as_retriever(similarity_top_k=payload.top_k * 2)

        for node_with_score in retriever.retrieve(payload.query):
            node = node_with_score.node
            category = str(node.metadata.get("category", "uncategorized"))
            if payload.category and category != payload.category:
                continue
            hits.append(
                LlamaSearchHit(
                    document_id=node.ref_doc_id or node.id_,
                    title=str(node.metadata.get("title", "Untitled")),
                    category=category,
                    score=node_with_score.score,
                    preview=node.text[:260],
                )
            )
            if len(hits) >= payload.top_k:
                break

        return LlamaSearchResponse(
            hits=hits,
            note="Powered by LlamaIndex VectorStoreIndex with local MockEmbedding for learning.",
        )


llama_store = LlamaCrudStore()
