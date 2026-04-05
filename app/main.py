"""
CELPIP Simulator API — FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError

from datetime import datetime
from app.api.v1.router import router as api_v1_router
from app.api.v1.webhooks import router as webhooks_router
from app.core.config import settings
from app.core.redis import init_redis, close_redis
from app.core.logger import logger

# Record startup time for uptime calculations
START_TIME = datetime.now()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_redis()
    yield
    # Shutdown
    await close_redis()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    tags_metadata = [
        {
            "name": "Users",
            "description": "Operations with users. Registering, updating, and administrative authorization.",
        },
        {
            "name": "Test Available",
            "description": "Access to CELPIP practice tests. Includes minimal names and full hierarchical views.",
        },
        {
            "name": "Answer Sheets",
            "description": "Submission and retrieval of user answer sheets for evaluation.",
        },
        {
            "name": "Test Results",
            "description": "Retrieval of scored test results, including CLB averages and individual skill scores.",
        },
        {
            "name": "Parts",
            "description": "Management of test parts (Listening, Reading, Writing, Speaking).",
        },
        {
            "name": "Sections",
            "description": "Management of sections within test parts.",
        },
        {
            "name": "Admin",
            "description": "Administrative actions, such as user authorization and advanced configuration.",
        },
        {
            "name": "Health",
            "description": "System health checks.",
        },
    ]

    app = FastAPI(
        title="CELPIP Simulator API",
        description="""
# CELPIP Simulator API
Backend API for the CELPIP Simulator practice platform.

## Features
- **Comprehensive CELPIP Tests**: Access listening, reading, writing, and speaking practice.
- **Automated Grading**: Instant results for multiple-choice questions.
- **Clerk Integration**: Secure authentication and user management.
- **Performance Tracking**: View history and CLB-aligned scoring.
        """,
        version="1.1.0",
        contact={
            "name": "Eduardo Matos",
            "url": "https://github.com/eduardomatos66",
        },
        openapi_tags=tags_metadata,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.APP_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(api_v1_router, prefix="/api/v1")
    app.include_router(webhooks_router, prefix="/webhooks")

    # Health check
    @app.get("/health", tags=["Health"])
    async def health() -> dict:
        """Liveness probe endpoint."""
        return {"status": "ok"}

    # Exception Handlers
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "status": exc.status_code,
                    "type": "HTTP Error",
                    "message": getattr(exc, "detail", str(exc)),
                    "details": None
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "status": 422,
                    "type": "Validation Error",
                    "message": "The request payload is invalid.",
                    "details": exc.errors()
                }
            }
        )

    @app.exception_handler(IntegrityError)
    async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
        # Catch safe constraints (duplicates etc.) instead of 500
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": {
                    "status": 409,
                    "type": "Conflict",
                    "message": "Data constraint violation or conflict.",
                    "details": None
                }
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "status": 500,
                    "type": "Internal Server Error",
                    "message": "An unexpected error occurred.",
                    "details": str(exc) if settings.APP_ENV == "development" else None
                }
            }
        )

    return app

app = create_app()
