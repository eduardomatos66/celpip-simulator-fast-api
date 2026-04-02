"""API v1 router — aggregates all resource routers."""

from fastapi import APIRouter, Depends
from app.core.deps import get_authorized_user
from app.api.v1 import (
    parts, sections, tests, answer_sheets, test_results, users,
    test_areas, check_db, admin, webhooks
)

router = APIRouter()

router.include_router(parts.router, prefix="/parts", tags=["Parts"], dependencies=[Depends(get_authorized_user)])
router.include_router(sections.router, prefix="/sections", tags=["Sections"], dependencies=[Depends(get_authorized_user)])
router.include_router(tests.router, prefix="/test-available", tags=["Tests"])
router.include_router(tests.router, prefix="/tests", tags=["Tests"], dependencies=[Depends(get_authorized_user)])

router.include_router(answer_sheets.router, prefix="/answer-sheets", tags=["Answer Sheets"], dependencies=[Depends(get_authorized_user)])
router.include_router(test_results.router, prefix="/test-results", tags=["Test Results"], dependencies=[Depends(get_authorized_user)])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(test_areas.router, prefix="/test-areas", tags=["Test Areas"], dependencies=[Depends(get_authorized_user)])
router.include_router(check_db.router, prefix="/check-db", tags=["Check DB"], dependencies=[Depends(get_authorized_user)])
router.include_router(admin.router, prefix="/admin", tags=["Admin"], dependencies=[Depends(get_authorized_user)])
router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
