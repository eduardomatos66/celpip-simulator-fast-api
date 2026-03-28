"""API v1 router — aggregates all resource routers."""

from fastapi import APIRouter

router = APIRouter()

from app.api.v1 import parts, sections, tests, answer_sheets, test_results, users, test_areas, check_db, admin, webhooks

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
