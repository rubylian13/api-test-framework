"""
test_products.py — API 1~4: Products & Brands
覆蓋：
  API 1  GET  /productsList     → 200
  API 2  POST /productsList     → 405 (method not allowed)
  API 3  GET  /brandsList       → 200
  API 4  PUT  /brandsList       → 405 (method not allowed)
"""
import pytest

from core.base_client import BaseClient
from core.api_endpoints import Endpoints, ResponseMessage
from core.schema_validator import SchemaValidator
from utils.assertions import ApiAssert


@pytest.mark.smoke
@pytest.mark.regression
class TestGetProductsList:
    """API 1: GET /api/productsList"""

    def test_status_code_is_200(self, client: BaseClient):
        resp = client.get(Endpoints.PRODUCTS_LIST)
        ApiAssert.status_ok(resp)

    def test_response_code_is_200(self, client: BaseClient):
        resp = client.get(Endpoints.PRODUCTS_LIST)
        ApiAssert.response_code_ok(resp)

    def test_returns_products_list(self, client: BaseClient):
        resp = client.get(Endpoints.PRODUCTS_LIST)
        ApiAssert.has_products(resp)

    def test_schema_is_valid(self, client: BaseClient):
        resp = client.get(Endpoints.PRODUCTS_LIST)
        SchemaValidator.validate_products_list(resp.body)

    def test_each_product_has_required_fields(self, client: BaseClient):
        resp = client.get(Endpoints.PRODUCTS_LIST)
        products = resp.products

        for product in products:
            assert "id" in product,    f"Missing 'id' in product: {product}"
            assert "name" in product,  f"Missing 'name' in product: {product}"
            assert "price" in product, f"Missing 'price' in product: {product}"
            assert "brand" in product, f"Missing 'brand' in product: {product}"

    def test_response_time_is_acceptable(self, client: BaseClient):
        resp = client.get(Endpoints.PRODUCTS_LIST)
        ApiAssert.response_time_under(resp, max_ms=5000)


@pytest.mark.negative
class TestPostProductsList:
    """API 2: POST /api/productsList → 應回傳 405"""

    def test_post_is_not_allowed(self, client: BaseClient):
        resp = client.post(Endpoints.PRODUCTS_LIST)
        ApiAssert.method_not_allowed(resp)

    def test_error_message_is_correct(self, client: BaseClient):
        resp = client.post(Endpoints.PRODUCTS_LIST)
        ApiAssert.message_equals(resp, ResponseMessage.METHOD_NOT_SUPPORTED)

    def test_error_schema_is_valid(self, client: BaseClient):
        resp = client.post(Endpoints.PRODUCTS_LIST)
        SchemaValidator.validate_error_response(resp.body)


@pytest.mark.smoke
@pytest.mark.regression
class TestGetBrandsList:
    """API 3: GET /api/brandsList"""

    def test_status_code_is_200(self, client: BaseClient):
        resp = client.get(Endpoints.BRANDS_LIST)
        ApiAssert.status_ok(resp)

    def test_response_code_is_200(self, client: BaseClient):
        resp = client.get(Endpoints.BRANDS_LIST)
        ApiAssert.response_code_ok(resp)

    def test_returns_brands_list(self, client: BaseClient):
        resp = client.get(Endpoints.BRANDS_LIST)
        ApiAssert.has_brands(resp)

    def test_schema_is_valid(self, client: BaseClient):
        resp = client.get(Endpoints.BRANDS_LIST)
        SchemaValidator.validate_brands_list(resp.body)

    def test_each_brand_has_id_and_name(self, client: BaseClient):
        resp = client.get(Endpoints.BRANDS_LIST)
        for brand in resp.brands:
            assert "id" in brand,    f"Missing 'id' in brand: {brand}"
            assert "brand" in brand, f"Missing 'brand' in brand: {brand}"

    def test_brand_names_are_non_empty(self, client: BaseClient):
        resp = client.get(Endpoints.BRANDS_LIST)
        empty = [b for b in resp.brands if not b.get("brand")]
        assert not empty, f"Found brands with empty name: {empty}"


@pytest.mark.negative
class TestPutBrandsList:
    """API 4: PUT /api/brandsList → 應回傳 405"""

    def test_put_is_not_allowed(self, client: BaseClient):
        resp = client.put(Endpoints.BRANDS_LIST)
        ApiAssert.method_not_allowed(resp)

    def test_error_message_is_correct(self, client: BaseClient):
        resp = client.put(Endpoints.BRANDS_LIST)
        ApiAssert.message_equals(resp, ResponseMessage.METHOD_NOT_SUPPORTED)
