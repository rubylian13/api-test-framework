"""
test_search.py — API 5~6: Search Product
覆蓋：
  API 5  POST /searchProduct  (含 search_product 參數)  → 200
  API 6  POST /searchProduct  (缺少 search_product)     → 400
"""
import pytest

from core.base_client import BaseClient
from core.api_endpoints import Endpoints, ResponseMessage
from core.schema_validator import SchemaValidator
from utils.assertions import ApiAssert


@pytest.mark.smoke
@pytest.mark.regression
class TestSearchProductPositive:
    """API 5: POST /searchProduct — 正向測試"""

    # ── Parametrize：同一邏輯跑多組資料 ─────────────
    @pytest.mark.parametrize("keyword", ["top", "tshirt", "jean", "dress"])
    def test_search_returns_results(self, client: BaseClient, keyword: str):
        resp = client.post(Endpoints.SEARCH_PRODUCT, data={"search_product": keyword})
        ApiAssert.success_response(resp)
        ApiAssert.has_products(resp)

    @pytest.mark.parametrize("keyword", ["top", "tshirt", "jean"])
    def test_search_results_contain_keyword(self, client: BaseClient, keyword: str):
        resp = client.post(Endpoints.SEARCH_PRODUCT, data={"search_product": keyword})
        ApiAssert.products_contain_keyword(resp, keyword)

    def test_search_schema_is_valid(self, client: BaseClient):
        resp = client.post(Endpoints.SEARCH_PRODUCT, data={"search_product": "top"})
        SchemaValidator.validate_products_list(resp.body)

    def test_search_with_uppercase_keyword(self, client: BaseClient):
        """大小寫應視為相同 keyword"""
        lower = client.post(Endpoints.SEARCH_PRODUCT, data={"search_product": "top"})
        upper = client.post(Endpoints.SEARCH_PRODUCT, data={"search_product": "TOP"})
        # 兩者的結果數量應相同（API 行為驗證）
        lower_count = len(lower.products or [])
        upper_count = len(upper.products or [])
        # 若 API 大小寫不敏感，數量應一致
        assert lower_count == upper_count, (
            f"Case sensitivity issue: 'top' returned {lower_count} results, "
            f"'TOP' returned {upper_count} results"
        )

    def test_search_response_time(self, client: BaseClient):
        resp = client.post(Endpoints.SEARCH_PRODUCT, data={"search_product": "top"})
        ApiAssert.response_time_under(resp, max_ms=5000)


@pytest.mark.negative
class TestSearchProductNegative:
    """API 6: POST /searchProduct — 缺少必要參數"""

    def test_missing_search_product_param_returns_400(self, client: BaseClient):
        resp = client.post(Endpoints.SEARCH_PRODUCT, data={})
        ApiAssert.status_ok(resp)
        ApiAssert.response_code_bad_request(resp)

    def test_missing_param_error_message(self, client: BaseClient):
        resp = client.post(Endpoints.SEARCH_PRODUCT, data={})
        ApiAssert.message_equals(resp, ResponseMessage.MISSING_SEARCH_PARAM)

    def test_missing_param_schema_valid(self, client: BaseClient):
        resp = client.post(Endpoints.SEARCH_PRODUCT, data={})
        SchemaValidator.validate_error_response(resp.body)

    def test_empty_string_search(self, client: BaseClient):
        """空字串 search_product 的行為"""
        resp = client.post(Endpoints.SEARCH_PRODUCT, data={"search_product": ""})
        # 有些 API 把空字串當作 missing，有些當作合法查詢
        # 這裡驗證 responseCode 是已知的值
        assert resp.response_code in (200, 400), (
            f"Unexpected responseCode for empty search: {resp.response_code}"
        )
