# CELPIP Simulator — FastAPI Backend

**CELPIP Simulator API** is the core backend service providing test questions, answer evaluation, and progression functionality for the CELPIP Simulator practice platform. It serves a 100% feature-complete replacement for the original Java architecture.

Below you will find the relevant project definitions, setup instructions, and testing guidelines.

## Tech Stack
- **Framework**: FastAPI (Python 3.9+)
- **ORM**: SQLAlchemy with Async support
- **Database**: TiDB (MySQL-compatible) via `PyMySQL` driver
- **Authentication**: Clerk JWT Verification
- **Testing**: `pytest` + `httpx` (async)
- **Migrations**: Alembic
- **Caching**: Redis
- **Data Validation**: Pydantic
- **Evaluation**: Automated HTML-Aware Grading (MCQ)

## Project Architecture
The project strictly follows a layered service-oriented architecture:
```text
celpip-simulator-fast-api/
├── app/
│   ├── api/v1/          # FastAPI routers (API Endpoints)
│   ├── core/            # Configuration, Security, DB session, Deps
│   ├── models/          # SQLAlchemy Database Entities (ORM)
│   ├── schemas/         # Pydantic validation (Request/Response DTOs)
│   └── services/        # Core business logic
├── alembic/             # Database migration configuration
├── tests/               # Unit and Integration test suites
└── docs/                # Project Documentation (like this README)
```

## Setup & Execution

### 1. Python Environment Setup
Ensure you have Python 3.9+ installed.
```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables
You must create a `.env` file at the root of the project with the following essential configuration:
```dotenv
# TiDB / MySQL Configuration
TIDB_USER=your_user
TIDB_PASSWORD=your_password
TIDB_HOST=your_host
TIDB_PORT=4000
TIDB_DATABASE=celpip_db
TIDB_SSL_CA=path_to_pem_or_empty

# Clerk Authentication
CLERK_JWKS_URL=https://[your-clerk-domain]/.well-known/jwks.json
CLERK_AUDIENCE=
CLERK_ISSUER_URL=https://[your-clerk-domain]
CLERK_SECRET_KEY=sk_test_...
CLERK_WEBHOOK_SECRET=whsec_...

# App Configuration
APP_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

### 3. Running the Server Locally
**Do NOT run `python app/main.py`.** Because of how Python module imports (`app.`) are structured, you must rely on the ASGI server (Uvicorn).

```bash
# Start the development server with live-reloading:
uvicorn app.main:app --reload
```
Once it's running, you can access the interactive API docs:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## DB Migrations (Alembic)
Changes to Pydantic/SQLAlchemy models should be migrated using Alembic to sync the database schema:
```bash
# Auto-generate a new migration script
alembic revision --autogenerate -m "description_of_change"

# Apply the migrations up to the latest revision
alembic upgrade head
```

---

## Authentication (Clerk)

The project uses **Clerk** for all user authentication. It relies on signed JWT (JSON Web Tokens) to secure private endpoints.

### How It Works
1. **JWT Verification**: The backend validates the `Authorization: Bearer <token>` header against Clerk's public JSON Web Key Set (JWKS).
2. **User Synchronization**: When an authenticated request is made (to `/api/v1/users/me` or other protected routes), the backend automatically verifies the user's `clerk_id`.
   - If the user doesn't exist in the local database (TiDB/MySQL), a new record is created on-the-fly.
   - If the user exists, their local record is retrieved.
3. **Requirement**: Ensure `CLERK_JWKS_URL` and `CLERK_AUDIENCE` are correctly set in your `.env` file.
- **Webhooks**: See the [Webhooks Setup Guide](file:///e:/Workspace/celpip-simulator-fast-api/docs/webhooks_setup.md) for automated user provisioning.
- **Scoring & Evaluation**: See the [Scoring and Evaluation Guide](file:///e:/Workspace/celpip-simulator-fast-api/docs/scoring_and_evaluation.md) for details on automated MCQ grading.

### Protected vs Public Routes

| Category | Authentication | Routes |
|---|---|---|
| **Public** | ❌ None | `GET /api/v1/tests`, `GET /api/v1/parts`, `GET /api/v1/tests/{id}` |
| **Protected** | ✅ Required | `POST /api/v1/answer-sheets/submit`, `GET /api/v1/users/me`, `GET /api/v1/test-results/user` |

---

## Testing

The project uses `pytest` for all unit and integration testing. Tests make use of an in-memory SQLite database locally to avoid touching the production TiDB instance. This ensures you can run tests offline securely.

### Execute the Core Test Suite
```bash
# Run all tests cleanly
pytest tests/ -v
```

### Global Error Handling in Tests
If you intend to test edge-case error injections (e.g., verifying a DB constraint 409 Conflict), the project uses a centralized error schema (`{"error": { "status": ..., "message": ... }}`). These scenarios are exclusively tested under `tests/integration/test_api_errors.py` to ensure raw HTML/500 panics never leak to the frontend.

---

## troubleshooting

### 1. CORS Policy Errors
If your frontend (e.g., Vite/React) cannot reach the backend, Ensure your origin is listed in `APP_CORS_ORIGINS` inside the `.env` file.
- **Example**: `APP_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]`

### 2. 503 Service Unavailable
If the backend returns a 503 error on protected routes, it usually means the **Clerk JWKS URL** is incorrect or inaccessible.
- Check that `CLERK_JWKS_URL` in `.env` points to a valid JSON endpoint.
- Ensure your internet connection can reach the Clerk API.

### 3. Database Connection Issues
If the server fails to start, verify your `TIDB_SSL_CA` path. If you are not using SSL (local dev), you can leave it empty, but the backend expects a valid path if a value is provided.
