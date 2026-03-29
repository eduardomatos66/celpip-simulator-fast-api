"""
Async-compatible SQLAlchemy engine and session factory for TiDB (MySQL).

Uses PyMySQL (pure Python) via SQLAlchemy's thread-executor bridge so no
C compiler or async MySQL driver is required.
"""

import os
import ssl
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings
from app.core.logger import logger


def _build_database_url() -> str:
    return (
        f"mysql+pymysql://{settings.TIDB_USER}:{settings.TIDB_PASSWORD}"
        f"@{settings.TIDB_HOST}:{settings.TIDB_PORT}/{settings.TIDB_DATABASE}"
    )


def _build_connect_args() -> dict:
    """Build SSL connect args for TiDB Cloud if a CA cert path is provided."""
    # If the CA file exists, use it to build a specific context
    if settings.TIDB_SSL_CA and os.path.exists(settings.TIDB_SSL_CA):
        ssl_ctx = ssl.create_default_context(cafile=settings.TIDB_SSL_CA)
        return {"ssl": ssl_ctx}

    # If the CA file is missing (common on Vercel) or we're in production,
    # we fall back to the system's default SSL context.
    # TiDB Cloud requires SSL, and this will use the system's root CAs.
    if settings.APP_ENV != "development" or settings.TIDB_SSL_CA:
        if settings.TIDB_SSL_CA:
            logger.warning(f"SSL CA file NOT FOUND at: {settings.TIDB_SSL_CA}. Falling back to default SSL context.")

        # PyMySQL expects an SSLContext object in the 'ssl' key to enable validation
        return {"ssl": ssl.create_default_context()}

    return {}


# Synchronous engine — wrapped by FastAPI via run_in_executor when needed
engine = create_engine(
    _build_database_url(),
    connect_args=_build_connect_args(),
    echo=settings.APP_ENV == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models."""
    pass


def get_db():
    """FastAPI dependency — yields a synchronous DB session."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
