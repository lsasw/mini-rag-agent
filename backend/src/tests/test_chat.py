"""
对话（RAG 问答）接口测试
"""
from fastapi.testclient import TestClient


class TestChat:
    """POST /api/chat — RAG 问答"""

    def test_chat_returns_answer_and_sources(self, client: TestClient):
        """正常提问应返回 answer、sources 和 mode 字段"""
        response = client.post("/api/chat", json={"message": "RAG 的核心流程是什么？"})
        assert response.status_code == 200

        data = response.json()
        assert "answer" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert "mode" in data
        assert data["mode"].startswith("rag:")

    def test_chat_with_agent_mode(self, client: TestClient):
        """Agent 模式应返回带 tool_notes 的回答"""
        response = client.post(
            "/api/chat",
            json={"message": "现在时间", "use_agent": True},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["mode"].startswith("agent:")

    def test_chat_empty_message_rejected(self, client: TestClient):
        """空消息应返回 422 验证错误"""
        response = client.post("/api/chat", json={"message": ""})
        assert response.status_code == 422

    def test_chat_batch_questions(self, client: TestClient):
        """批量提问应全部成功"""
        questions = [
            "什么是 RAG？",
            "LangChain 是什么？",
            "如何上传文档？",
        ]
        for question in questions:
            response = client.post("/api/chat", json={"message": question})
            assert response.status_code == 200
            assert len(response.json()["answer"]) > 0
