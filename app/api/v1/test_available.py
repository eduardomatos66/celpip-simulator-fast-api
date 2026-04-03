from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import redis.asyncio as redis
from app.core.deps import get_db, AuthorizedUser
from app.core.redis import get_redis
from app.schemas.quiz import TestAvailableRead, TestAvailableMinimalRead
from app.services import test_service

router = APIRouter()

@router.get("",
    response_model=List[TestAvailableMinimalRead],
    summary="List All Available Tests (Names Only)",
    description="Retrieve a list of all available CELPIP tests, providing only the test ID and name.")
async def get_all_test_available(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    # Use the optimized minimal query service
    tests = await test_service.get_tests_minimal_cached(db, redis_client)
    return tests


@router.get("/{test_id}",
    response_model=TestAvailableRead,
    summary="Get Full Test Content",
    description="Retrieve the complete hierarchical structure of a specific test, including areas, parts, sections, questions, and all options.",
    responses={404: {"description": "Test not found"}})
async def get_test_detailed(
    test_id: int,
    user: AuthorizedUser,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    test_av = await test_service.get_test_available_by_id_cached(db, redis_client, test_id=test_id)
    if not test_av:
        raise HTTPException(status_code=404, detail="Test not found")
    return test_av
