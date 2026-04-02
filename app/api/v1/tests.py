from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import redis.asyncio as redis
from app.core.deps import get_db
from app.core.redis import get_redis
from app.schemas.quiz import TestAvailableRead
from app.services import test_service

router = APIRouter()

@router.get("", response_model=List[TestAvailableRead])
async def get_tests(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """List all available CELPIP tests (summary only)."""
    tests = await test_service.get_tests_summary_cached(db, redis_client)
    return tests


@router.get("/all", response_model=List[TestAvailableRead])
def get_all_tests_full(
    db: Session = Depends(get_db)
):
    """Retrieve all tests with their full hierarchy."""
    return test_service.get_tests_full(db)


@router.get("/{test_id}", response_model=TestAvailableRead)
async def get_test(
    test_id: int,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Retrieve full details for a specific test (areas, parts, sections)."""
    test_av = await test_service.get_test_available_by_id_cached(db, redis_client, test_id=test_id)
    if not test_av:
        raise HTTPException(status_code=404, detail="Test not found")
    return test_av
