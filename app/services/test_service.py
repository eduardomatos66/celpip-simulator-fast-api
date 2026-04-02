from typing import List, Optional
import json
import redis.asyncio as redis
from sqlalchemy.orm import Session, joinedload
from fastapi.concurrency import run_in_threadpool
from fastapi.encoders import jsonable_encoder
from app.models.quiz import TestAvailable, TestArea, Part, Section, Question, Option, AreaTest
from app.schemas.quiz import TestAvailableRead
from app.core.decorators import log_execution_time

@log_execution_time
def get_test_available_by_id(db: Session, test_id: int) -> Optional[TestAvailable]:
    """Retrieve a specific test with its full hierarchy."""
    return db.query(TestAvailable).options(
        joinedload(TestAvailable.test_areas).joinedload(TestArea.part).joinedload(Part.introduction),
        joinedload(TestAvailable.test_areas).joinedload(TestArea.part).joinedload(Part.sections).joinedload(Section.questions).joinedload(Question.options)
    ).filter(TestAvailable.test_id == test_id).first()

@log_execution_time
def get_tests_summary(db: Session) -> List[TestAvailable]:
    """Retrieve a summary list of tests without deep eager loading."""
    return db.query(TestAvailable).options(
        joinedload(TestAvailable.test_areas)
    ).all()

@log_execution_time
async def get_test_available_by_id_cached(db: Session, redis_client: redis.Redis, test_id: int) -> Optional[dict]:
    cache_key = f"cache:tests:{test_id}"

    if redis_client:
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

    test_data = await run_in_threadpool(get_test_available_by_id, db, test_id)
    if not test_data:
        return None

    test_schema = TestAvailableRead.model_validate(test_data).model_dump(mode="json")

    if redis_client:
        await redis_client.set(cache_key, json.dumps(test_schema), ex=3600)

    return test_schema

@log_execution_time
async def get_tests_summary_cached(db: Session, redis_client: redis.Redis) -> List[dict]:
    cache_key = "cache:tests:summary"

    if redis_client:
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

    tests_data = await run_in_threadpool(get_tests_summary, db)
    tests_schema = [TestAvailableRead.model_validate(t).model_dump(mode="json") for t in tests_data]

    if redis_client:
        await redis_client.set(cache_key, json.dumps(tests_schema), ex=3600)

    return tests_schema

@log_execution_time
def get_tests_full(db: Session) -> List[TestAvailable]:
    """Retrieve all tests with their full hierarchy."""
    return db.query(TestAvailable).options(
        joinedload(TestAvailable.test_areas).joinedload(TestArea.part).joinedload(Part.introduction),
        joinedload(TestAvailable.test_areas).joinedload(TestArea.part).joinedload(Part.sections).joinedload(Section.questions).joinedload(Question.options)
    ).all()
