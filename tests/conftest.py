"""
Pytest fixtures shared across all tests.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.core.deps import get_db

from sqlalchemy.pool import StaticPool

# Synchronous SQLite in-memory engine for model testing
engine = create_engine(
    "sqlite:///:memory:", 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """Create and drop tables for testing."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Yield a database session for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


from app.core.deps import get_db, get_current_user_claims

@pytest.fixture
async def client() -> AsyncClient:
    """Async HTTP test client wired to the FastAPI ASGI app."""
    # Override the dependency to use the test DB and Mock Auth
    app.dependency_overrides[get_db] = lambda: TestingSessionLocal()
    app.dependency_overrides[get_current_user_claims] = lambda: {"sub": "test_clerk", "email": "test@example.com"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()


@pytest.fixture
async def unauth_client() -> AsyncClient:
    """Unauthenticated Async HTTP test client wired to the FastAPI ASGI app with mocked DB."""
    app.dependency_overrides[get_db] = lambda: TestingSessionLocal()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()
