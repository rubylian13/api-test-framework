"""
User Data Factory
職責：動態產生 test data，確保每次測試資料唯一、乾淨
面試重點：展示 Factory pattern，避免 test data 衝突
"""
import random
import string
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

try:
    from faker import Faker
    _faker = Faker()
    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False


def _rand_str(n: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=n))


@dataclass
class UserPayload:
    """
    對應 API 11/13 的完整 user 欄位
    使用 dataclass 方便轉 dict 傳給 requests
    """
    name: str
    email: str
    password: str
    title: str = "Mr"
    birth_date: str = "15"
    birth_month: str = "6"
    birth_year: str = "1990"
    firstname: str = "Test"
    lastname: str = "User"
    company: str = "TSMC"
    address1: str = "123 Test Street"
    address2: str = "Apt 4"
    country: str = "Taiwan"
    zipcode: str = "300"
    state: str = "Hsinchu"
    city: str = "Hsinchu City"
    mobile_number: str = "0912345678"

    def to_dict(self) -> dict:
        return asdict(self)


class UserFactory:
    """
    動態產生 UserPayload，每次呼叫皆不同
    """

    @staticmethod
    def create(
        email: Optional[str] = None,
        password: Optional[str] = None,
        **overrides,
    ) -> UserPayload:
        """
        建立一個隨機、唯一的 user payload
        可透過 overrides 覆蓋任意欄位
        """
        ts = int(time.time() * 1000) % 100000  # 短 timestamp

        if HAS_FAKER:
            name      = _faker.name()
            firstname = _faker.first_name()
            lastname  = _faker.last_name()
        else:
            name      = f"Test User {ts}"
            firstname = "Test"
            lastname  = f"User{ts}"

        payload = UserPayload(
            name=name,
            email=email or f"test_{ts}_{_rand_str(5)}@example.com",
            password=password or f"Pass@{_rand_str(6)}!",
            firstname=firstname,
            lastname=lastname,
            **overrides,
        )
        return payload

    @staticmethod
    def create_minimal(email: str, password: str) -> dict:
        """只有 email + password 的精簡版，用於 auth 測試"""
        return {"email": email, "password": password}

    @staticmethod
    def invalid_email_payload(password: str = "Test1234!") -> dict:
        """缺少 email 的 payload，用於 negative 測試"""
        return {"password": password}

    @staticmethod
    def invalid_password_payload(email: str) -> dict:
        """缺少 password 的 payload"""
        return {"email": email}
