"""
共享的测试夹具（fixtures）和工具函数。

使用 TestClient 不需要启动服务器，直接模拟 HTTP 请求。
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> TestClient:
    """返回一个 FastAPI TestClient 实例，每个测试函数独立使用。"""
    return TestClient(app)
