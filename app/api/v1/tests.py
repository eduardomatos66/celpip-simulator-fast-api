from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.quiz import TestAvailableRead
from app.services import test_service

router = APIRouter()

@router.get("/", response_model=List[TestAvailableRead])
def get_tests(db: Session = Depends(get_db)):
    """List all available CELPIP tests (summary only)."""
    tests = test_service.get_tests_summary(db)
    return tests

@router.get("/{test_id}", response_model=TestAvailableRead)
def get_test(test_id: int, db: Session = Depends(get_db)):
    """Retrieve full details for a specific test (areas, parts, sections)."""
    test_av = test_service.get_test_available_by_id(db, test_id=test_id)
    if not test_av:
        raise HTTPException(status_code=404, detail="Test not found")
    return test_av
