"""API v1 router — aggregates all resource routers."""

from fastapi import APIRouter, Depends
from app.core.deps import get_authorized_user
from app.api.v1 import (
    parts, sections, answer_sheets, test_results, users,
    test_areas, check_db, admin, webhooks, test_available
)

router = APIRouter()

router.include_router(parts.router, prefix="/parts", tags=["Parts"], dependencies=[Depends(get_authorized_user)])
router.include_router(sections.router, prefix="/sections", tags=["Sections"], dependencies=[Depends(get_authorized_user)])
router.include_router(test_available.router, prefix="/test-available", tags=["Test Available"])

router.include_router(answer_sheets.router, prefix="/answer-sheets", tags=["Answer Sheets"], dependencies=[Depends(get_authorized_user)])
router.include_router(test_results.router, prefix="/test-results", tags=["Test Results"], dependencies=[Depends(get_authorized_user)])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(test_areas.router, prefix="/test-areas", tags=["Test Areas"], dependencies=[Depends(get_authorized_user)])
router.include_router(check_db.router, prefix="/check-db", tags=["Check DB"], dependencies=[Depends(get_authorized_user)])
router.include_router(admin.router, prefix="/admin", tags=["Admin"], dependencies=[Depends(get_authorized_user)])
router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
