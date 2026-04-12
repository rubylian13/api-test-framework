"""
BaseClient — HTTP 封裝層
職責：
  - 統一管理 base_url、headers、timeout
  - 封裝 requests session，支援 retry
  - 記錄每次 request/response log
  - 回傳結構化 ApiResponse，讓 tests 不直接碰 requests
"""
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.api_endpoints import BASE_URL

logger = logging.getLogger(__name__)


@dataclass
class ApiResponse:
    """
    統一 response 結構，讓 assertion 有一致的操作介面
    """
    status_code: int
    body: Any                          # parsed JSON 或 raw text
    headers: dict = field(default_factory=dict)
    elapsed_ms: float = 0.0

    # ── 便利屬性 ──────────────────────────────────
    @property
    def response_code(self) -> Optional[int]:
        """取 body 中的 responseCode（此 API 的特殊設計）"""
        if isinstance(self.body, dict):
            return self.body.get("responseCode")
        return None

    @property
    def message(self) -> Optional[str]:
        """取 body 中的 message"""
        if isinstance(self.body, dict):
            return self.body.get("message")
        return None

    @property
    def products(self) -> Optional[list]:
        if isinstance(self.body, dict):
            return self.body.get("products")
        return None

    @property
    def brands(self) -> Optional[list]:
        if isinstance(self.body, dict):
            return self.body.get("brands")
        return None

    def __repr__(self):
        return (
            f"ApiResponse(status={self.status_code}, "
            f"responseCode={self.response_code}, "
            f"elapsed={self.elapsed_ms:.0f}ms)"
        )


class BaseClient:
    """
    所有 API 呼叫的統一入口
    面試重點：展示 session 管理、retry 機制、統一 logging
    """

    DEFAULT_TIMEOUT = 10  # seconds

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = self._build_session()

    # ── Session 建立（含 retry 策略）────────────────
    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    # ── 核心 HTTP 方法 ────────────────────────────
    def get(self, endpoint: str, params: dict = None, **kwargs) -> ApiResponse:
        return self._request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: dict = None, json: dict = None, **kwargs) -> ApiResponse:
        return self._request("POST", endpoint, data=data, json=json, **kwargs)

    def put(self, endpoint: str, data: dict = None, **kwargs) -> ApiResponse:
        return self._request("PUT", endpoint, data=data, **kwargs)

    def delete(self, endpoint: str, data: dict = None, **kwargs) -> ApiResponse:
        return self._request("DELETE", endpoint, data=data, **kwargs)

    # ── 私有：實際送出 request ────────────────────
    def _request(self, method: str, endpoint: str, **kwargs) -> ApiResponse:
        url = self.base_url + endpoint
        timeout = kwargs.pop("timeout", self.DEFAULT_TIMEOUT)

        logger.info(f"→ {method} {url}")
        if kwargs.get("data"):
            logger.debug(f"  payload: {kwargs['data']}")

        resp = self.session.request(method, url, timeout=timeout, **kwargs)

        # 解析 body
        try:
            body = resp.json()
        except Exception:
            body = resp.text

        api_resp = ApiResponse(
            status_code=resp.status_code,
            body=body,
            headers=dict(resp.headers),
            elapsed_ms=resp.elapsed.total_seconds() * 1000,
        )
        logger.info(f"← {api_resp}")
        return api_resp

    def close(self):
        self.session.close()
