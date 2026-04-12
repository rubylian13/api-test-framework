"""
Custom Assertion Helpers
職責：語意化的 assertion，讓測試 code 像自然語言
面試重點：展示 clean test code，可讀性高、失敗訊息清晰
"""
from core.base_client import ApiResponse
from core.api_endpoints import HttpStatus


class ApiAssert:
    """
    所有 API 斷言集中在此，提供有意義的 failure message
    """

    # ── HTTP Status ───────────────────────────────
    @staticmethod
    def status_ok(resp: ApiResponse):
        assert resp.status_code == HttpStatus.OK, (
            f"Expected HTTP 200, got {resp.status_code}\nbody: {resp.body}"
        )

    @staticmethod
    def status_created(resp: ApiResponse):
        assert resp.status_code == HttpStatus.CREATED, (
            f"Expected HTTP 201, got {resp.status_code}\nbody: {resp.body}"
        )

    # ── responseCode in body ─────────────────────
    @staticmethod
    def response_code_is(resp: ApiResponse, expected: int):
        actual = resp.response_code
        assert actual == expected, (
            f"Expected responseCode={expected}, got {actual}\n"
            f"message: {resp.message}"
        )

    @staticmethod
    def response_code_ok(resp: ApiResponse):
        ApiAssert.response_code_is(resp, 200)

    @staticmethod
    def response_code_created(resp: ApiResponse):
        ApiAssert.response_code_is(resp, 201)

    @staticmethod
    def response_code_method_not_allowed(resp: ApiResponse):
        ApiAssert.response_code_is(resp, 405)

    @staticmethod
    def response_code_bad_request(resp: ApiResponse):
        ApiAssert.response_code_is(resp, 400)

    @staticmethod
    def response_code_not_found(resp: ApiResponse):
        ApiAssert.response_code_is(resp, 404)

    # ── Message ───────────────────────────────────
    @staticmethod
    def message_equals(resp: ApiResponse, expected: str):
        assert resp.message == expected, (
            f"Expected message='{expected}', got '{resp.message}'"
        )

    @staticmethod
    def message_contains(resp: ApiResponse, substring: str):
        msg = resp.message or ""
        assert substring in msg, (
            f"Expected message to contain '{substring}', got '{msg}'"
        )

    # ── Body 結構 ─────────────────────────────────
    @staticmethod
    def has_products(resp: ApiResponse):
        assert resp.products is not None, "Response missing 'products' key"
        assert len(resp.products) > 0, "Products list is empty"

    @staticmethod
    def has_brands(resp: ApiResponse):
        assert resp.brands is not None, "Response missing 'brands' key"
        assert len(resp.brands) > 0, "Brands list is empty"

    @staticmethod
    def products_contain_keyword(resp: ApiResponse, keyword: str):
        """確認搜尋結果中至少一個產品名稱含有關鍵字（不分大小寫）"""
        products = resp.products or []
        assert len(products) > 0, f"No products found for keyword '{keyword}'"
        kw = keyword.lower()
        matched = [
            p for p in products
            if kw in p.get("name", "").lower()
            or kw in p.get("category", {}).get("category", "").lower()
        ]
        assert len(matched) > 0, (
            f"No product name/category contains '{keyword}' in results: "
            f"{[p.get('name') for p in products[:5]]}"
        )

    # ── Performance ──────────────────────────────
    @staticmethod
    def response_time_under(resp: ApiResponse, max_ms: float):
        assert resp.elapsed_ms <= max_ms, (
            f"Response too slow: {resp.elapsed_ms:.0f}ms > {max_ms}ms"
        )

    # ── Composite（常用組合）─────────────────────
    @staticmethod
    def success_response(resp: ApiResponse):
        """HTTP 200 + responseCode 200"""
        ApiAssert.status_ok(resp)
        ApiAssert.response_code_ok(resp)

    @staticmethod
    def method_not_allowed(resp: ApiResponse):
        """HTTP 200 + responseCode 405 + 正確訊息"""
        from core.api_endpoints import ResponseMessage
        ApiAssert.status_ok(resp)
        ApiAssert.response_code_method_not_allowed(resp)
        ApiAssert.message_equals(resp, ResponseMessage.METHOD_NOT_SUPPORTED)
