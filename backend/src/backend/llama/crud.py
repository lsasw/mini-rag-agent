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

# 配置 LlamaIndex 全局设置：不使用真实 LLM，用 MockEmbedding 模拟向量化
Settings.llm = None
Settings.embed_model = MockEmbedding(embed_dim=64)


class LlamaCrudStore:
    """基于 LlamaIndex VectorStoreIndex 的文档 CRUD 存储。

    同时维护两份数据：
    1. JSON 文件 — 持久化文档的完整内容（用于列表展示和恢复）
    2. LlamaIndex 内存索引 — 用于语义检索
    """

    def __init__(self) -> None:
        # 延迟构建索引，首次访问时才从 JSON 文件恢复
        self._index: VectorStoreIndex | None = None

    @property
    def data_path(self) -> Path:
        """获取 JSON 数据文件路径，文件不存在时自动创建空数组。"""
        path = get_settings().data_dir / "llama_documents.json"
        if not path.exists():
            path.write_text("[]", encoding="utf-8")
        return path

    def _read(self) -> list[LlamaDocument]:
        """从 JSON 文件读取所有文档。"""
        raw = json.loads(self.data_path.read_text(encoding="utf-8"))
        return [LlamaDocument(**item) for item in raw]

    def _write(self, documents: list[LlamaDocument]) -> None:
        """将所有文档写入 JSON 文件。"""
        self.data_path.write_text(
            json.dumps([document.model_dump() for document in documents], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _to_llama_doc(self, document: LlamaDocument) -> Document:
        """将业务模型转换为 LlamaIndex 的 Document 对象。"""
        return Document(
            text=document.content,
            id_=document.id,
            metadata={"title": document.title, "category": document.category},
        )

    def _ensure_index(self) -> VectorStoreIndex:
        """确保索引已构建（懒加载），从 JSON 文件恢复所有文档并构建向量索引。"""
        if self._index is None:
            llama_documents = [self._to_llama_doc(document) for document in self._read()]
            self._index = VectorStoreIndex.from_documents(llama_documents)
        return self._index

    # ---- 分类操作 ----

    def list_categories(self) -> list[str]:
        """列出所有不重复的分类名称，按字母排序。"""
        return sorted({document.category for document in self._read()})

    # ---- 文档 CRUD ----

    def list_documents(self, category: str | None = None) -> list[LlamaDocument]:
        """列出文档，可按分类过滤。"""
        documents = self._read()
        if category:
            return [document for document in documents if document.category == category]
        return documents

    def create_document(self, payload: LlamaDocumentCreate) -> LlamaDocument:
        """创建文档：写入 JSON 文件，同时插入 LlamaIndex 索引。"""
        document = LlamaDocument(
            id=str(uuid.uuid4()),
            title=payload.title,
            category=payload.category,
            content=payload.content,
        )
        documents = self._read()
        documents.append(document)
        self._write(documents)

        # LlamaIndex 新增：将新文档节点插入已有索引
        self._ensure_index().insert(self._to_llama_doc(document))
        return document

    def update_document(self, document_id: str, payload: LlamaDocumentUpdate) -> LlamaDocument | None:
        """更新文档：更新 JSON 文件中的记录，并替换索引中的旧节点。"""
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

        # LlamaIndex 更新：update_ref_doc 会删除旧节点并插入新节点
        self._ensure_index().update_ref_doc(self._to_llama_doc(updated))
        return updated

    def delete_document(self, document_id: str) -> bool:
        """删除文档：从 JSON 文件和索引中同时移除。"""
        documents = self._read()
        if not any(document.id == document_id for document in documents):
            return False

        self._write([document for document in documents if document.id != document_id])

        # LlamaIndex 删除：从索引和 docstore 中移除该文档的所有节点
        self._ensure_index().delete_ref_doc(document_id, delete_from_docstore=True)
        return True

    # ---- 检索 ----

    def search(self, payload: LlamaSearchRequest) -> LlamaSearchResponse:
        """语义检索：使用 LlamaIndex 的 retriever 进行向量相似度搜索。

        检索策略：先取 top_k * 2 条候选结果，再按分类过滤，最终返回 top_k 条。
        """
        index = self._ensure_index()
        hits: list[LlamaSearchHit] = []
        # 多取一些候选，以便分类过滤后仍有足够结果
        retriever = index.as_retriever(similarity_top_k=payload.top_k * 2)

        for node_with_score in retriever.retrieve(payload.query):
            node = node_with_score.node
            category = str(node.metadata.get("category", "uncategorized"))
            # 如果指定了分类，过滤不匹配的结果
            if payload.category and category != payload.category:
                continue
            hits.append(
                LlamaSearchHit(
                    document_id=node.ref_doc_id or node.id_,
                    title=str(node.metadata.get("title", "Untitled")),
                    category=category,
                    score=node_with_score.score,
                    preview=node.text[:260],  # 截取前 260 字符作为预览
                )
            )
            if len(hits) >= payload.top_k:
                break

        return LlamaSearchResponse(
            hits=hits,
            note="Powered by LlamaIndex VectorStoreIndex with local MockEmbedding for learning.",
        )


# 全局单例，供路由层直接使用
llama_store = LlamaCrudStore()
