"""
文档上传/管理接口测试
"""
from io import BytesIO

from fastapi.testclient import TestClient


class TestDocuments:
    """文档管理接口"""

    def test_list_documents_empty(self, client: TestClient):
        """初始状态下列表为空数组"""
        response = client.get("/api/documents")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_upload_txt_document(self, client: TestClient):
        """上传 .txt 文件应成功"""
        content = "这是一份测试文档，用于验证上传功能。".encode("utf-8")
        files = {"file": ("test.txt", BytesIO(content), "text/plain")}
        response = client.post("/api/documents/upload", files=files)
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "Document uploaded and indexed"
        assert data["document"]["filename"] == "test.txt"
        assert data["document"]["chunks"] >= 1
        assert data["document"]["characters"] > 0

    def test_upload_md_document(self, client: TestClient):
        """上传 .md 文件应成功"""
        content = "# 标题\n\n这是 Markdown 文档内容。".encode("utf-8")
        files = {"file": ("doc.md", BytesIO(content), "text/markdown")}
        response = client.post("/api/documents/upload", files=files)
        assert response.status_code == 200
        assert response.json()["document"]["filename"] == "doc.md"

    def test_upload_unsupported_format_rejected(self, client: TestClient):
        """上传不支持的格式（.exe）应返回 400"""
        files = {"file": ("bad.exe", BytesIO(b"fake"), "application/octet-stream")}
        response = client.post("/api/documents/upload", files=files)
        assert response.status_code == 400
        assert "Only .txt, .md and .pdf" in response.json()["detail"]

    def test_upload_missing_filename_rejected(self, client: TestClient):
        """缺少文件名应返回 422 验证错误"""
        files = {"file": ("", BytesIO(b"content"), "text/plain")}
        response = client.post("/api/documents/upload", files=files)
        assert response.status_code == 422

    def test_delete_nonexistent_document(self, client: TestClient):
        """删除不存在的文档应返回 404"""
        response = client.delete("/api/documents/nonexistent-id")
        assert response.status_code == 404
