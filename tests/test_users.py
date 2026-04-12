"""
test_users.py — API 11~14: User CRUD
覆蓋：
  API 11  POST    /createAccount          → 201
  API 12  DELETE  /deleteAccount          → 200
  API 13  PUT     /updateAccount          → 200
  API 14  GET     /getUserDetailByEmail   → 200
"""
import pytest

from core.base_client import BaseClient
from core.api_endpoints import Endpoints, ResponseCode, ResponseMessage
from core.schema_validator import SchemaValidator
from data.user_factory import UserFactory
from utils.assertions import ApiAssert


@pytest.mark.regression
@pytest.mark.crud
class TestCreateAccount:
    """API 11: POST /api/createAccount"""

    def test_create_user_returns_201(self, client: BaseClient, new_user_payload: dict):
        resp = client.post(Endpoints.CREATE_ACCOUNT, data=new_user_payload)
        ApiAssert.status_ok(resp)
        ApiAssert.response_code_created(resp)

        # teardown：清除剛建的 user
        client.delete(Endpoints.DELETE_ACCOUNT, data={
            "email": new_user_payload["email"],
            "password": new_user_payload["password"],
        })

    def test_create_user_message(self, client: BaseClient, new_user_payload: dict):
        resp = client.post(Endpoints.CREATE_ACCOUNT, data=new_user_payload)
        ApiAssert.message_equals(resp, ResponseMessage.USER_CREATED)

        client.delete(Endpoints.DELETE_ACCOUNT, data={
            "email": new_user_payload["email"],
            "password": new_user_payload["password"],
        })

    def test_create_duplicate_user_returns_error(
        self, client: BaseClient, registered_user: dict
    ):
        """
        用已存在的 email 重複建立 → 應回傳 error
        面試重點：duplicate 情境的 negative test
        """
        payload = UserFactory.create(
            email=registered_user["email"],
            password=registered_user["password"],
        ).to_dict()
        resp = client.post(Endpoints.CREATE_ACCOUNT, data=payload)
        # API 文件沒有明確定義，但應是 error（非 201）
        assert resp.response_code != ResponseCode.CREATED, (
            "Should not create duplicate user, but got responseCode=201"
        )

    def test_create_user_missing_required_fields(self, client: BaseClient):
        """缺少必要欄位"""
        minimal = {"email": "incomplete@example.com"}
        resp = client.post(Endpoints.CREATE_ACCOUNT, data=minimal)
        assert resp.response_code != ResponseCode.CREATED, (
            "Should fail when required fields are missing"
        )


@pytest.mark.regression
@pytest.mark.crud
class TestDeleteAccount:
    """API 12: DELETE /api/deleteAccount"""

    def test_delete_existing_user(self, client: BaseClient):
        """建立 → 刪除，整個 lifecycle 驗證"""
        user = UserFactory.create()
        payload = user.to_dict()

        # 先建立
        create_resp = client.post(Endpoints.CREATE_ACCOUNT, data=payload)
        assert create_resp.response_code == ResponseCode.CREATED

        # 再刪除
        del_resp = client.delete(Endpoints.DELETE_ACCOUNT, data={
            "email": user.email,
            "password": user.password,
        })
        ApiAssert.success_response(del_resp)
        ApiAssert.message_equals(del_resp, ResponseMessage.USER_DELETED)

    def test_delete_nonexistent_user(self, client: BaseClient):
        """刪除不存在的 user"""
        resp = client.delete(Endpoints.DELETE_ACCOUNT, data={
            "email": "ghost_user_xyz@example.com",
            "password": "SomePass123!",
        })
        # 應回傳 error（非 200 success）
        assert resp.response_code != ResponseCode.SUCCESS, (
            "Deleting non-existent user should not return success"
        )


@pytest.mark.regression
@pytest.mark.crud
class TestUpdateAccount:
    """API 13: PUT /api/updateAccount"""

    def test_update_existing_user(self, client: BaseClient, registered_user: dict):
        """更新已存在 user 的資料"""
        update_payload = UserFactory.create(
            email=registered_user["email"],
            password=registered_user["password"],
        ).to_dict()
        update_payload["name"] = "Updated Name TSMC"
        update_payload["city"] = "Taipei"

        resp = client.put(Endpoints.UPDATE_ACCOUNT, data=update_payload)
        ApiAssert.success_response(resp)
        ApiAssert.message_equals(resp, ResponseMessage.USER_UPDATED)

    def test_update_nonexistent_user(self, client: BaseClient):
        """更新不存在的 user"""
        payload = UserFactory.create(
            email="ghost_update@example.com",
        ).to_dict()
        resp = client.put(Endpoints.UPDATE_ACCOUNT, data=payload)
        assert resp.response_code != ResponseCode.SUCCESS, (
            "Updating non-existent user should not return success"
        )


@pytest.mark.smoke
@pytest.mark.crud
class TestGetUserDetail:
    """API 14: GET /api/getUserDetailByEmail"""

    def test_get_existing_user_returns_200(
        self, client: BaseClient, registered_user: dict
    ):
        resp = client.get(
            Endpoints.GET_USER_DETAIL,
            params={"email": registered_user["email"]},
        )
        ApiAssert.success_response(resp)

    def test_get_user_detail_schema(
        self, client: BaseClient, registered_user: dict
    ):
        resp = client.get(
            Endpoints.GET_USER_DETAIL,
            params={"email": registered_user["email"]},
        )
        SchemaValidator.validate_user_detail(resp.body)

    def test_get_user_returns_correct_email(
        self, client: BaseClient, registered_user: dict
    ):
        resp = client.get(
            Endpoints.GET_USER_DETAIL,
            params={"email": registered_user["email"]},
        )
        user_in_body = resp.body.get("user", {})
        assert user_in_body.get("email") == registered_user["email"], (
            f"Expected email={registered_user['email']}, "
            f"got {user_in_body.get('email')}"
        )

    def test_get_nonexistent_user_returns_404(self, client: BaseClient):
        resp = client.get(
            Endpoints.GET_USER_DETAIL,
            params={"email": "nobody_xyz@example.com"},
        )
        ApiAssert.response_code_not_found(resp)

    def test_get_user_without_email_param(self, client: BaseClient):
        """缺少 email 參數"""
        resp = client.get(Endpoints.GET_USER_DETAIL, params={})
        # 應回傳 error
        assert resp.response_code in (400, 404), (
            f"Expected 400 or 404, got {resp.response_code}"
        )


@pytest.mark.regression
@pytest.mark.crud
class TestUserLifecycle:
    """
    端對端的 User CRUD lifecycle 測試
    面試重點：展示 E2E 思維，涵蓋 create → read → update → delete
    """

    def test_full_user_crud_lifecycle(self, client: BaseClient):
        user = UserFactory.create()
        creds = {"email": user.email, "password": user.password}

        # 1. CREATE
        create = client.post(Endpoints.CREATE_ACCOUNT, data=user.to_dict())
        assert create.response_code == ResponseCode.CREATED, (
            f"Step 1 Create failed: {create.body}"
        )

        # 2. READ — 驗證剛建的 user 可以查到
        read = client.get(Endpoints.GET_USER_DETAIL, params={"email": user.email})
        assert read.response_code == ResponseCode.SUCCESS, (
            f"Step 2 Read failed: {read.body}"
        )
        assert read.body["user"]["email"] == user.email

        # 3. UPDATE — 修改 city
        update_payload = user.to_dict()
        update_payload["city"] = "New Taipei City"
        update = client.put(Endpoints.UPDATE_ACCOUNT, data=update_payload)
        assert update.response_code == ResponseCode.SUCCESS, (
            f"Step 3 Update failed: {update.body}"
        )

        # 4. VERIFY UPDATE — 再查一次確認更新生效
        read2 = client.get(Endpoints.GET_USER_DETAIL, params={"email": user.email})
        assert read2.response_code == ResponseCode.SUCCESS

        # 5. DELETE
        delete = client.delete(Endpoints.DELETE_ACCOUNT, data=creds)
        assert delete.response_code == ResponseCode.SUCCESS, (
            f"Step 5 Delete failed: {delete.body}"
        )
        assert delete.message == ResponseMessage.USER_DELETED

        # 6. VERIFY DELETE — 確認 user 已不存在
        verify = client.get(Endpoints.GET_USER_DETAIL, params={"email": user.email})
        assert verify.response_code == ResponseCode.NOT_FOUND, (
            f"Step 6 Verify delete failed: user still exists! {verify.body}"
        )
