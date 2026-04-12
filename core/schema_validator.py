"""
Schema Validator
職責：定義各 API 的 JSON Schema，並提供驗證方法
面試重點：驗證 response 結構，而非只看 status code
"""
import jsonschema


# ── JSON Schemas ──────────────────────────────────────────────────────────────

PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "price", "brand", "category"],
    "properties": {
        "id":       {"type": "integer"},
        "name":     {"type": "string", "minLength": 1},
        "price":    {"type": "string"},
        "brand":    {"type": "string"},
        "category": {
            "type": "object",
            "required": ["usertype", "category"],
        },
    },
}

PRODUCTS_LIST_SCHEMA = {
    "type": "object",
    "required": ["responseCode", "products"],
    "properties": {
        "responseCode": {"type": "integer", "enum": [200]},
        "products": {
            "type": "array",
            "minItems": 1,
            "items": PRODUCT_SCHEMA,
        },
    },
}

BRAND_SCHEMA = {
    "type": "object",
    "required": ["id", "brand"],
    "properties": {
        "id":    {"type": "integer"},
        "brand": {"type": "string", "minLength": 1},
    },
}

BRANDS_LIST_SCHEMA = {
    "type": "object",
    "required": ["responseCode", "brands"],
    "properties": {
        "responseCode": {"type": "integer", "enum": [200]},
        "brands": {
            "type": "array",
            "minItems": 1,
            "items": BRAND_SCHEMA,
        },
    },
}

ERROR_SCHEMA = {
    "type": "object",
    "required": ["responseCode", "message"],
    "properties": {
        "responseCode": {"type": "integer"},
        "message":      {"type": "string"},
    },
}

USER_DETAIL_SCHEMA = {
    "type": "object",
    "required": ["responseCode", "user"],
    "properties": {
        "responseCode": {"type": "integer", "enum": [200]},
        "user": {
            "type": "object",
            "required": ["id", "name", "email"],
            "properties": {
                "id":    {"type": "integer"},
                "name":  {"type": "string"},
                "email": {"type": "string", "format": "email"},
            },
        },
    },
}


# ── Validator ─────────────────────────────────────────────────────────────────

class SchemaValidator:
    """
    包裝 jsonschema.validate，提供有意義的 assertion 訊息
    """

    @staticmethod
    def validate(instance: dict, schema: dict, context: str = "") -> None:
        try:
            jsonschema.validate(instance=instance, schema=schema)
        except jsonschema.ValidationError as e:
            prefix = f"[{context}] " if context else ""
            raise AssertionError(
                f"{prefix}Schema validation failed:\n"
                f"  path:    {' -> '.join(str(p) for p in e.absolute_path)}\n"
                f"  message: {e.message}\n"
                f"  value:   {e.instance}"
            ) from e

    @staticmethod
    def validate_products_list(body: dict):
        SchemaValidator.validate(body, PRODUCTS_LIST_SCHEMA, "products list")

    @staticmethod
    def validate_brands_list(body: dict):
        SchemaValidator.validate(body, BRANDS_LIST_SCHEMA, "brands list")

    @staticmethod
    def validate_error_response(body: dict):
        SchemaValidator.validate(body, ERROR_SCHEMA, "error response")

    @staticmethod
    def validate_user_detail(body: dict):
        SchemaValidator.validate(body, USER_DETAIL_SCHEMA, "user detail")
