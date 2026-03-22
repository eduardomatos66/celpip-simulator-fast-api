# CELPIP Simulator — FastAPI Development Plan

**Version**: 1.2.0
**Date**: 2026-03-22
**Status**: Completed/Ready

---

End-to-end development of the CELPIP Simulator backend in Python with FastAPI. The project follows a strict **Document → Implement → Test → Commit** cycle on every patch.

---

## Development Principles

> Every patch must follow this cycle, no exceptions:
> 1. **Document** — update docstrings / OpenAPI descriptions
> 2. **Implement** — write the code
> 3. **Test** — write/run unit or integration tests
> 4. **Commit** — `git commit -m "feat|fix|chore: ..."` with conventional commits

---

## Phase 1 — Project Scaffolding

Set up the full directory structure and tooling before writing any domain code.

### Project Structure
```
celpip-simulator-fast-api/
├── app/
│   ├── main.py                  # FastAPI app factory
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # APIRouter aggregator
│   │       ├── parts.py
│   │       ├── sections.py
│   │       ├── questions.py
│   │       ├── tests.py
│   │       ├── answer_sheets.py
│   │       ├── test_results.py
│   │       └── users.py
│   ├── core/
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   └── security.py          # Clerk JWT verification
│   ├── models/                  # SQLAlchemy ORM models
│   ├── schemas/                 # Pydantic request/response schemas
│   └── services/                # Business logic layer
├── alembic/                     # DB migrations
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── docs/                        # Project documentation
├── .env.example
├── requirements.txt
├── pytest.ini
└── README.md
```

### Files Created
- `requirements.txt` — fastapi, uvicorn, sqlalchemy, aiomysql, alembic, pydantic-settings, python-jose, pytest, httpx
- `app/main.py` — app factory with CORS, routers, health endpoint
- `app/core/config.py` — `Settings` class via `pydantic-settings`
- `.env.example` — all required environment variables documented
- `pytest.ini` — test configuration

### Commit
```
git commit -m "chore: project scaffolding and tooling setup"
```

---

## Phase 2 — SQLAlchemy Models (Entities)

Map all domain entities to SQLAlchemy ORM models, mirroring the existing database schema.

### Entity Map

| Model | Table | Key Fields |
|-------|-------|-----------|
| `User` | `users` | `id`, `full_name`, `email`, `clerk_id`, `created_at`, `updated_at` |
| `PartIntroduction` | `part_introduction` | `id`, `text`, `auxiliary_texts` |
| `Part` | `part` | `id`, `part_number`, `part_name`, `text_question_content`, `time`, `questions_type`, `introduction_id` |
| `Section` | `section` | `id`, `section_number`, `text`, `time`, `section_audio_link`, `section_image_link`, `section_video_link`, `text_question_content` |
| `Question` | `question` | `id`, `question_number`, `time`, `audio_link`, `text` |
| `Option` | `question_option` | `id`, `text`, `is_correct` |
| `TestArea` | `test_area` | `id`, `area` (enum: listening/reading/writing/speaking), `part_id` |
| `TestAvailable` | `test_available` | `id`, `test_name` |
| `AnswerSheet` | `answer_sheet` | `id`, `test_id`, `user_id`, `date` |
| `OptionAnswer` | `option_answer` | `id`, `question_id`, `user_answer`, `correct_answer`, `duration` |
| `TestResult` | `test_result` | `id`, `listening_corrects`, `listening_max`, `reading_corrects`, `reading_max`, `writing_min`, `writing_max`, `speaking_min`, `speaking_max`, `clb_min`, `clb_max`, `clb_average`, `result_date`, `test_available_id`, `user_id`, `answer_sheet_id` |

### Files
- [NEW] `app/models/__init__.py`
- [NEW] `app/models/user.py`
- [NEW] `app/models/quiz.py` — `PartIntroduction`, `Option`, `Question`, `Section`, `Part`, `TestArea`, `TestAvailable`
- [NEW] `app/models/answer.py` — `OptionAnswer`, `AnswerSheet`, `TestResult`

### Alembic Migrations
```bash
alembic init alembic
alembic revision --autogenerate -m "create initial schema"
alembic upgrade head
```

### Tests
- Unit tests for all models: `tests/unit/test_models.py`
  - Assert table name, column types, nullable constraints, relationships

### Commit
```
git commit -m "feat: add SQLAlchemy models for all domain entities"
```

---

## Phase 3 — TiDB Connection

Configure the async database connection to TiDB (MySQL-compatible).

### Connection Strategy
- **Driver**: `PyMySQL` (pure Python MySQL driver, TiDB-compatible)
- **SQLAlchemy**: `create_engine`
- **Session**: `Session` via `sessionmaker` (synchronous, bridged for FastAPI)
- **TLS**: TiDB Cloud requires SSL — configure `ssl={"ssl_ca": ...}` in connection args

### Files
- [MODIFY] `app/core/config.py` — add `TIDB_HOST`, `TIDB_PORT`, `TIDB_USER`, `TIDB_PASSWORD`, `TIDB_DATABASE`, `TIDB_SSL_CA`
- [MODIFY] `app/core/database.py` — async engine with SSL context
- [NEW] `app/core/deps.py` — `get_db()` FastAPI dependency yielding `AsyncSession`

### Tests
- Integration test: `tests/integration/test_database.py`
  - Assert connection to TiDB is alive (`SELECT 1`)
  - Requires valid `.env` with TiDB credentials

### Commit
```
git commit -m "feat: configure async TiDB connection with SSL"
```

---

## Phase 4 — Business Logic (Services)

Implement the service layer with all business rules.

### Services

#### `QuizService` — `app/services/quiz_service.py`
- `get_all_parts()` → list of parts with sections, questions, options
- `get_part_by_id(part_id)` → single part or raise 404
- `create_part(data)`, `update_part(part_id, data)`, `delete_part(part_id)`
- Same CRUD pattern for `Section`, `Question`, `Option`

#### `TestService` — `app/services/test_service.py`
- `get_all_tests()` → list summary DTOs
- `get_test_by_id(test_id)` → full test with all areas, parts, sections, questions
- `get_all_test_data()` → full payload list

#### `AnswerSheetService` — `app/services/answer_sheet_service.py`
- `get_by_id(sheet_id)` → answer sheet or 404
- `submit(data, user_id)` → validate, persist, trigger scoring

#### `TestResultService` — `app/services/test_result_service.py`
- `calculate_result(answer_sheet_id)` → compute CLB scores (clb_min / clb_max / clb_average)
- `get_results_for_user(user_id)`, `get_result(test_id, user_id)`, `delete(result_id)`

#### `UserService` — `app/services/user_service.py`
- `get_or_create_by_clerk_id(clerk_id, email, full_name)` → upsert on first Clerk login
- `get_by_email(email)` → user or 404

### Pydantic Schemas
One file per domain in `app/schemas/`: `quiz.py`, `answer.py`, `user.py`
- `*Base`, `*Create`, `*Update`, `*Read` schemas per entity

### Tests
- Unit tests per service in `tests/unit/services/`
  - Use `AsyncMock` / `MagicMock` for DB session
  - Test happy path, 404, and validation edge cases

### Commit
```
git commit -m "feat: implement business logic service layer"
```

---

## Phase 5 — REST API

Wire up FastAPI routers using the service layer.

### Endpoints

| Router | Method | Path | Description |
|--------|--------|------|-------------|
| `parts` | GET | `/api/v1/parts` | List all parts |
| `parts` | GET | `/api/v1/parts/{id}` | Get part by ID |
| `parts` | POST | `/api/v1/parts` | Create part |
| `parts` | PUT | `/api/v1/parts/{id}` | Update part |
| `parts` | DELETE | `/api/v1/parts/{id}` | Delete part |
| `sections` | GET/POST/PUT/DELETE | `/api/v1/sections/...` | Section CRUD |
| `tests` | GET | `/api/v1/tests` | List available tests |
| `tests` | GET | `/api/v1/tests/{id}` | Get full test data |
| `tests` | GET | `/api/v1/tests/all` | All tests with full data |
| `answer-sheets` | GET | `/api/v1/answer-sheets/{id}` | Get answer sheet |
| `answer-sheets` | POST | `/api/v1/answer-sheets/submit` | Submit answers |
| `test-results` | GET | `/api/v1/test-results/user/{email}` | User results |
| `test-results` | POST | `/api/v1/test-results/result` | Get specific result |
| `test-results` | DELETE | `/api/v1/test-results/{id}` | Delete result |
| `users` | GET | `/api/v1/users/me` | Current user profile |

### Files
- [NEW] `app/api/v1/parts.py`, `sections.py`, `tests.py`, `answer_sheets.py`, `test_results.py`, `users.py`
- [MODIFY] `app/api/v1/router.py` — aggregate all routers

### Tests
- Integration tests: `tests/integration/test_api_*.py`
  - Use `httpx.AsyncClient` with ASGI transport
  - Test 200, 404, 422 validation errors per endpoint

### Commit
```
git commit -m "feat: implement REST API endpoints for all resources"
```

---

## Phase 6 — Authentication (Clerk)

Secure all endpoints with Clerk JWT verification.

### How It Works
1. Frontend authenticates with Clerk → receives a signed JWT
2. JWT sent as `Authorization: Bearer <token>`
3. API fetches Clerk's JWKS and verifies the signature
4. Decoded claims (`sub`, `email`, `name`) → `get_or_create` local `User`

> No passwords are stored. Clerk owns all authentication.

### Files
- [MODIFY] `app/core/config.py` — add `CLERK_JWKS_URL`, `CLERK_AUDIENCE`
- [MODIFY] `app/core/security.py` — `verify_clerk_token(token: str) -> dict`
- [NEW] `app/core/deps.py` — `get_current_user()` FastAPI dependency
- [MODIFY] All routers — `Depends(get_current_user)` on protected routes

### Protected vs Public Routes

| Route | Auth |
|-------|------|
| `GET /api/v1/tests` | ❌ Public |
| `GET /api/v1/tests/{id}` | ❌ Public |
| `GET /api/v1/parts` | ❌ Public |
| `POST /api/v1/answer-sheets/submit` | ✅ Required |
| `GET /api/v1/answer-sheets/{id}` | ✅ Required |
| `GET /api/v1/test-results/user/{email}` | ✅ Required |
| `GET /api/v1/users/me` | ✅ Required |

### Tests
- `tests/unit/test_security.py` — mock JWKS, assert valid/expired/invalid tokens

### Commit
```
git commit -m "feat: add Clerk JWT authentication with JWKS verification"
```

---

## Verification Plan

### Automated Tests
```bash
pip install -r requirements.txt
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Manual Verification
```bash
uvicorn app.main:app --reload
# Swagger UI: http://localhost:8000/docs
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-03-22 | Phase 1 completed. Switched to pure Python `PyMySQL` driver. |
| 1.0.0 | 2026-03-22 | Initial plan — 6 phases defined |
