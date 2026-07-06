"""
LlamaIndex CRUD 接口测试
"""
from fastapi.testclient import TestClient


class TestLlamaCategories:
    """GET /api/llama/categories — 分类列表"""

    def test_list_categories(self, client: TestClient):
        """获取分类列表应返回 200"""
        response = client.get("/api/llama/categories")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestLlamaDocuments:
    """LlamaIndex 文档 CRUD"""

    def test_create_and_list_document(self, client: TestClient):
        """创建文档后应能在列表中查到"""
        payload = {
            "title": "LangChain 入门",
            "category": "tutorial",
            "content": "LangChain 是一个用于构建 LLM 应用的框架。",
        }
        # 创建
        resp = client.post("/api/llama/documents", json=payload)
        assert resp.status_code == 200
        doc_id = resp.json()["id"]
        assert resp.json()["title"] == payload["title"]

        # 列表
        resp = client.get("/api/llama/documents")
        assert resp.status_code == 200
        doc_ids = [doc["id"] for doc in resp.json()]
        assert doc_id in doc_ids

    def test_create_document_empty_title_rejected(self, client: TestClient):
        """空标题应返回 422"""
        payload = {"title": "", "category": "test", "content": "内容"}
        resp = client.post("/api/llama/documents", json=payload)
        assert resp.status_code == 422

    def test_update_document(self, client: TestClient):
        """更新文档标题和内容"""
        # 先创建
        create_payload = {
            "title": "原始标题",
            "category": "rag",
            "content": "原始内容",
        }
        resp = client.post("/api/llama/documents", json=create_payload)
        doc_id = resp.json()["id"]

        # 更新
        update_payload = {
            "title": "更新后的标题",
            "category": "rag",
            "content": "更新后的内容",
        }
        resp = client.put(f"/api/llama/documents/{doc_id}", json=update_payload)
        assert resp.status_code == 200
        assert resp.json()["title"] == update_payload["title"]
        assert resp.json()["content"] == update_payload["content"]

    def test_update_nonexistent_document(self, client: TestClient):
        """更新不存在的文档应返回 404"""
        payload = {"title": "标题", "category": "rag", "content": "内容"}
        resp = client.put("/api/llama/documents/fake-id", json=payload)
        assert resp.status_code == 404

    def test_delete_document(self, client: TestClient):
        """删除文档应成功，再次删除应 404"""
        # 创建
        payload = {"title": "待删除", "category": "tmp", "content": "临时内容"}
        resp = client.post("/api/llama/documents", json=payload)
        doc_id = resp.json()["id"]

        # 删除
        resp = client.delete(f"/api/llama/documents/{doc_id}")
        assert resp.status_code == 200
        assert resp.json()["deleted"] is True

        # 再次删除应 404
        resp = client.delete(f"/api/llama/documents/{doc_id}")
        assert resp.status_code == 404


class TestLlamaSearch:
    """POST /api/llama/search — 语义检索"""

    def test_search_returns_results(self, client: TestClient):
        """搜索应返回 hits 列表"""
        # 先创建一篇文档，确保索引中有数据
        client.post("/api/llama/documents", json={
            "title": "RAG 入门指南",
            "category": "rag",
            "content": "RAG（检索增强生成）是一种结合检索和生成的 AI 技术，能有效减少模型幻觉。",
        })

        resp = client.post("/api/llama/search", json={
            "query": "RAG",
            "top_k": 3,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "hits" in data
        assert isinstance(data["hits"], list)

    def test_search_with_category_filter(self, client: TestClient):
        """按分类过滤搜索"""
        resp = client.post("/api/llama/search", json={
            "query": "AI",
            "category": "rag",
            "top_k": 2,
        })
        assert resp.status_code == 200
        # 所有结果应属于 rag 分类或无结果
        for hit in resp.json()["hits"]:
            assert hit["category"] == "rag"

    def test_search_empty_query_rejected(self, client: TestClient):
        """空查询应返回 422"""
        resp = client.post("/api/llama/search", json={"query": ""})
        assert resp.status_code == 422
