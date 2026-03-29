"""API v1 router — aggregates all resource routers."""

from fastapi import APIRouter

router = APIRouter()

from typing import List
from app.api.v1 import (
    parts, sections, tests, answer_sheets, test_results, users,
    test_areas, check_db, admin, webhooks
)
from app.services import test_service
from app.core.deps import get_db
from app.core.redis import get_redis
from app.schemas.quiz import TestAvailableRead
from sqlalchemy.orm import Session
from fastapi import Depends
import redis.asyncio as redis

router.include_router(parts.router, prefix="/parts", tags=["Parts"])
router.include_router(sections.router, prefix="/sections", tags=["Sections"])
router.include_router(tests.router, prefix="/tests", tags=["Tests"])
router.include_router(answer_sheets.router, prefix="/answer-sheets", tags=["Answer Sheets"])
router.include_router(test_results.router, prefix="/test-results", tags=["Test Results"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(test_areas.router, prefix="/test-areas", tags=["Test Areas"])
router.include_router(check_db.router, prefix="/check-db", tags=["Check DB"])
router.include_router(admin.router, prefix="/admin", tags=["Admin"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

@router.get("/test-available", response_model=List[TestAvailableRead], tags=["Tests"])
async def get_test_available_root_compatibility(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Compatibility: Root-level alias for listing available tests."""
    return await test_service.get_tests_summary_cached(db, redis_client)
