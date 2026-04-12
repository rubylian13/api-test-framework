"""
API Endpoints 路由常數
集中管理所有 endpoint，避免 URL 散落在測試中
"""

BASE_URL = "https://automationexercise.com"


class Endpoints:
    # ── Products ─────────────────────────────────
    PRODUCTS_LIST   = "/api/productsList"
    BRANDS_LIST     = "/api/brandsList"
    SEARCH_PRODUCT  = "/api/searchProduct"

    # ── Auth ──────────────────────────────────────
    VERIFY_LOGIN    = "/api/verifyLogin"

    # ── Users ─────────────────────────────────────
    CREATE_ACCOUNT  = "/api/createAccount"
    DELETE_ACCOUNT  = "/api/deleteAccount"
    UPDATE_ACCOUNT  = "/api/updateAccount"
    GET_USER_DETAIL = "/api/getUserDetailByEmail"


class HttpStatus:
    OK              = 200
    CREATED         = 201
    BAD_REQUEST     = 400
    NOT_FOUND       = 404
    METHOD_NOT_ALLOWED = 405


class ResponseCode:
    """
    AutomationExercise 自訂的 responseCode
    注意：此 API 的 HTTP status code 固定是 200，
    實際結果在 JSON body 的 responseCode 欄位
    """
    SUCCESS             = 200
    CREATED             = 201
    BAD_REQUEST         = 400
    NOT_FOUND           = 404
    METHOD_NOT_ALLOWED  = 405


class ResponseMessage:
    USER_EXISTS         = "User exists!"
    USER_NOT_FOUND      = "User not found!"
    USER_CREATED        = "User created!"
    USER_DELETED        = "Account deleted!"
    USER_UPDATED        = "User updated!"
    EMAIL_EXISTS        = "Email already exists!"
    METHOD_NOT_SUPPORTED = "This request method is not supported."
    MISSING_SEARCH_PARAM = "Bad request, search_product parameter is missing in POST request."
    MISSING_EMAIL_PARAM  = "Bad request, email or password parameter is missing in POST request."
