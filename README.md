# API Test Automation Framework

A layered API test automation framework built with Python, pytest, and requests — targeting the [AutomationExercise](https://automationexercise.com/api_list) RESTful API (14 endpoints).

Designed with production-grade patterns: JSON Schema validation, Data Factory, custom semantic assertions, and CI/CD-ready test markers.

---

## Features

- **Layered architecture** — `core` / `data` / `utils` / `tests`, each with a single responsibility
- **JSON Schema validation** — detects API contract changes beyond status code checks
- **Data Factory pattern** — generates unique test data per run, enabling safe parallel execution
- **Semantic assertions** — `ApiAssert.success_response(resp)` reads like a specification
- **Full CRUD lifecycle** — Create → Read → Update → Delete with automatic teardown via pytest fixtures
- **CI/CD markers** — `smoke` for PR gates, `regression` for nightly builds

---

## Project Structure

```
api_test_framework/
├── core/
│   ├── base_client.py        # HTTP session, retry, unified request/response
│   ├── api_endpoints.py      # All route constants, status codes, messages
│   └── schema_validator.py   # JSON Schema definitions + validation helpers
├── data/
│   └── user_factory.py       # Dynamic test data generation (Factory pattern)
├── utils/
│   ├── assertions.py         # Semantic assertion helpers (ApiAssert)
│   └── logger.py             # Structured logging setup
├── tests/
│   ├── conftest.py           # Session-scoped fixtures, setup/teardown
│   ├── test_products.py      # API 1–4: Products & Brands
│   ├── test_search.py        # API 5–6: Search (parametrize)
│   ├── test_auth.py          # API 7–10: Login & Verify
│   └── test_users.py         # API 11–14: CRUD + lifecycle test
├── pytest.ini
└── requirements.txt
```

---

## Test Coverage

| Module | APIs | Test types |
|---|---|---|
| Products & Brands | 1–4 | Positive, negative, schema, performance |
| Search | 5–6 | Parametrize, boundary, case-sensitivity |
| Auth / Login | 7–10 | Valid, missing params, wrong method, invalid creds |
| User CRUD | 11–14 | Create, read, update, delete, full lifecycle E2E |

---

## Getting Started

**1. Clone and install**

```bash
git clone https://github.com/your-username/api-test-framework.git
cd api-test-framework
pip install -r requirements.txt
```

**2. Run all tests**

```bash
pytest tests/ -v
```

**3. Run by marker**

```bash
# Smoke tests only (fast, for PR gates)
pytest tests/ -m smoke -v

# Negative tests only
pytest tests/ -m negative -v

# Auth-related tests
pytest tests/ -m auth -v
```

**4. Generate Allure report**

```bash
pip install allure-pytest
pytest tests/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

---

## Design Decisions

### Why a layered architecture?

Each layer has one job. When the base URL changes, only `core/base_client.py` needs updating. When an assertion needs reuse across test files, it lives in `utils/assertions.py` — not duplicated. This separation makes the framework maintainable as the test suite grows.

### Why JSON Schema validation?

Status code checks alone miss silent breaking changes — a renamed field (`products` → `items`), a type change (`id: int` → `id: string`), or a missing required key. `SchemaValidator` catches these at the structure level on every run.

```python
# Not just this:
assert resp.status_code == 200

# But also this:
SchemaValidator.validate_products_list(resp.body)
```

### Why Data Factory instead of static fixtures?

Static test data creates coupling between tests — a user created in one test can cause a "duplicate email" failure in another. `UserFactory.create()` generates a unique email per call using a timestamp suffix, so tests are fully isolated and safe to run in parallel.

```python
# Every call returns fresh, unique data
user = UserFactory.create()    # test_abc123@example.com
user = UserFactory.create()    # test_def456@example.com
```

### Why custom assertions?

`ApiAssert` methods encode domain knowledge — the fact that this API always returns HTTP 200 but carries the real result in `responseCode` inside the JSON body. This detail doesn't belong scattered across 40 test functions.

```python
# Readable, reusable, failure message included
ApiAssert.success_response(resp)
ApiAssert.message_equals(resp, ResponseMessage.USER_EXISTS)
```

---

## CI/CD Integration

Tests are structured for pipeline use. A minimal GitHub Actions config:

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -m smoke -v
      - run: pytest tests/ -v
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.9+ | Language |
| pytest | Test runner, fixtures, markers |
| requests | HTTP client |
| jsonschema | JSON Schema validation |
| Faker | Realistic test data generation |
| Allure | Test reporting (optional) |

---

## API Reference

Base URL: `https://automationexercise.com`

Full endpoint list: [automationexercise.com/api_list](https://automationexercise.com/api_list)
