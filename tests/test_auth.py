"""
test_auth.py — API 7~10: Verify Login
覆蓋：
  API 7   POST   /verifyLogin  (valid credentials)      → 200
  API 8   POST   /verifyLogin  (missing email)          → 400
  API 9   DELETE /verifyLogin                           → 405
  API 10  POST   /verifyLogin  (invalid credentials)   → 404
"""
import pytest

from core.base_client import BaseClient
from core.api_endpoints import Endpoints, ResponseMessage
from core.schema_validator import SchemaValidator
from data.user_factory import UserFactory
from utils.assertions import ApiAssert


@pytest.mark.smoke
@pytest.mark.auth
class TestVerifyLoginValid:
    """API 7: POST /verifyLogin — 正確帳號密碼"""

    def test_valid_login_returns_200(self, client: BaseClient, registered_user: dict):
        resp = client.post(Endpoints.VERIFY_LOGIN, data=registered_user)
        ApiAssert.success_response(resp)

    def test_valid_login_message(self, client: BaseClient, registered_user: dict):
        resp = client.post(Endpoints.VERIFY_LOGIN, data=registered_user)
        ApiAssert.message_equals(resp, ResponseMessage.USER_EXISTS)

    def test_valid_login_schema(self, client: BaseClient, registered_user: dict):
        resp = client.post(Endpoints.VERIFY_LOGIN, data=registered_user)
        SchemaValidator.validate_error_response(resp.body)  # {responseCode, message}

    def test_valid_login_response_time(self, client: BaseClient, registered_user: dict):
        resp = client.post(Endpoints.VERIFY_LOGIN, data=registered_user)
        ApiAssert.response_time_under(resp, max_ms=5000)


@pytest.mark.negative
@pytest.mark.auth
class TestVerifyLoginMissingParams:
    """API 8: POST /verifyLogin — 缺少 email"""

    def test_missing_email_returns_400(self, client: BaseClient):
        payload = UserFactory.invalid_email_payload()
        resp = client.post(Endpoints.VERIFY_LOGIN, data=payload)
        ApiAssert.status_ok(resp)
        ApiAssert.response_code_bad_request(resp)

    def test_missing_email_error_message(self, client: BaseClient):
        payload = UserFactory.invalid_email_payload()
        resp = client.post(Endpoints.VERIFY_LOGIN, data=payload)
        ApiAssert.message_equals(resp, ResponseMessage.MISSING_EMAIL_PARAM)

    def test_missing_password_returns_400(self, client: BaseClient):
        payload = UserFactory.invalid_password_payload("test@example.com")
        resp = client.post(Endpoints.VERIFY_LOGIN, data=payload)
        ApiAssert.status_ok(resp)
        ApiAssert.response_code_bad_request(resp)

    def test_empty_body_returns_400(self, client: BaseClient):
        resp = client.post(Endpoints.VERIFY_LOGIN, data={})
        ApiAssert.response_code_bad_request(resp)


@pytest.mark.negative
@pytest.mark.auth
class TestVerifyLoginDeleteMethod:
    """API 9: DELETE /verifyLogin → 405"""

    def test_delete_method_not_allowed(self, client: BaseClient):
        resp = client.delete(Endpoints.VERIFY_LOGIN)
        ApiAssert.method_not_allowed(resp)

    def test_delete_error_message(self, client: BaseClient):
        resp = client.delete(Endpoints.VERIFY_LOGIN)
        ApiAssert.message_equals(resp, ResponseMessage.METHOD_NOT_SUPPORTED)


@pytest.mark.negative
@pytest.mark.auth
class TestVerifyLoginInvalidCredentials:
    """API 10: POST /verifyLogin — 錯誤帳號密碼"""

    def test_invalid_credentials_returns_404(self, client: BaseClient):
        payload = {
            "email": "nonexistent@example.com",
            "password": "WrongPass999!",
        }
        resp = client.post(Endpoints.VERIFY_LOGIN, data=payload)
        ApiAssert.status_ok(resp)
        ApiAssert.response_code_not_found(resp)

    def test_invalid_credentials_message(self, client: BaseClient):
        payload = {
            "email": "nonexistent@example.com",
            "password": "WrongPass999!",
        }
        resp = client.post(Endpoints.VERIFY_LOGIN, data=payload)
        ApiAssert.message_equals(resp, ResponseMessage.USER_NOT_FOUND)

    @pytest.mark.parametrize("email,password", [
        ("not-an-email", "somepassword"),
        ("", "somepassword"),
        ("test@example.com", ""),
    ])
    def test_boundary_invalid_inputs(
        self, client: BaseClient, email: str, password: str
    ):
        """邊界值測試：格式不正確的 email 或空字串"""
        payload = {"email": email, "password": password}
        resp = client.post(Endpoints.VERIFY_LOGIN, data=payload)
        # 回傳 400 或 404 都是合理的 error response
        assert resp.response_code in (400, 404), (
            f"Unexpected responseCode={resp.response_code} "
            f"for email='{email}', password='{password}'"
        )
