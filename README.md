# CELPIP Simulator API

A **FastAPI**-powered backend for the CELPIP Simulator — a practice platform for the Canadian English Language Proficiency Index Program (CELPIP) test.

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Language | Python 3.11+ |
| Server | Uvicorn (ASGI) |
| ORM | SQLAlchemy / Alembic |
| Auth | JWT (OAuth2 Bearer) |
| Docs | Swagger UI / ReDoc (auto-generated) |

---

## 📋 Prerequisites

- Python 3.11+
- `pip` or `poetry`
- PostgreSQL (or compatible database)

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/celpip-simulator-fast-api.git
cd celpip-simulator-fast-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your database credentials and secret keys
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the development server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## 📚 API Documentation

Once running, interactive docs are available at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🗂️ Project Structure

```
celpip-simulator-fast-api/
├── app/
│   ├── main.py           # FastAPI app entry point
│   ├── api/              # Route handlers (controllers)
│   ├── core/             # Config, security, dependencies
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # Business logic layer
│   └── db/               # Database session & base
├── alembic/              # Database migrations
├── tests/                # Unit & integration tests
├── .env.example          # Environment variable template
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🧪 Running Tests

```bash
pytest
```

---

## 🐳 Docker (optional)

```bash
docker build -t celpip-simulator-api .
docker run -p 8000:8000 --env-file .env celpip-simulator-api
```

---

## 📄 License

This project is licensed under the MIT License.
