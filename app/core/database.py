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
    # Option 1: File based SSL (most explicit)
    if settings.TIDB_SSL_CA and os.path.exists(settings.TIDB_SSL_CA):
        logger.info(f"Using file-based SSL configuration with: {settings.TIDB_SSL_CA}")
        # PyMySQL supports a dictionary for 'ssl' that includes the CA path
        # sqlalchemy connect_args passes this directly to pymysql.connect
        return {"ssl": {"ca": os.path.abspath(settings.TIDB_SSL_CA)}}

    # Option 2: Fallback for environments without the file (e.g. Vercel dashboard env missing the file)
    # We MUST force SSL if not in development or if a CA was explicitly requested by name
    if settings.APP_ENV != "development" or settings.TIDB_SSL_CA:
        if settings.TIDB_SSL_CA:
            logger.warning(f"SSL CA file NOT FOUND at: {settings.TIDB_SSL_CA}. Using default SSL context.")
        else:
            logger.info("Enforcing SSL for production environment using default context.")

        # Using a proper SSLContext object is the second best way to ensure secure transport
        return {"ssl": ssl.create_default_context()}

    # Option 3: Development without SSL (only if explicitly local/dev)
    logger.debug("Connecting to database without SSL (Development mode).")
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
