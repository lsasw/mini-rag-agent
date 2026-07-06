"""
健康检查接口测试
"""
from fastapi.testclient import TestClient


class TestHealth:
    """GET /api/health — 健康检查"""

    def test_health_returns_ok(self, client: TestClient):
        """健康检查应返回 200 和 status: ok"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
