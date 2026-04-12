"""
conftest.py — 共用 fixtures
pytest 自動載入，所有 test 都可直接使用

面試重點：
  - session-scoped client：整個測試跑一個 HTTP session
  - registered_user：建立用後自動清除（teardown）
  - allure 報告整合
"""
import pytest

from core.base_client import BaseClient
from core.api_endpoints import Endpoints, ResponseCode
from data.user_factory import UserFactory
from utils.logger import setup_logger

# 啟動 logging
setup_logger("INFO")


# ── Client Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client() -> BaseClient:
    """
    Session 級別的 BaseClient，整個測試 session 共用一個
    避免反覆建立 TCP 連線
    """
    c = BaseClient()
    yield c
    c.close()


# ── User Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def registered_user(client: BaseClient) -> dict:
    """
    建立一個真實存在的 user，session 結束後自動刪除
    回傳 dict: {"email": ..., "password": ...}

    面試重點：展示 setup/teardown，保持測試環境乾淨
    """
    user = UserFactory.create()
    payload = user.to_dict()

    resp = client.post(Endpoints.CREATE_ACCOUNT, data=payload)
    assert resp.response_code in (
        ResponseCode.CREATED, ResponseCode.SUCCESS
    ), f"Failed to create test user: {resp.body}"

    credentials = {"email": user.email, "password": user.password}
    yield credentials

    # ── Teardown: 刪除測試用 user ──────────────────
    client.delete(Endpoints.DELETE_ACCOUNT, data=credentials)


@pytest.fixture
def new_user_payload() -> dict:
    """每個 test 都拿到全新的 user payload（function scope）"""
    return UserFactory.create().to_dict()
