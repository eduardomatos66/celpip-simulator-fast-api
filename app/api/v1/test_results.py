from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, AuthorizedUser
from app.schemas.answer import TestResultRead, TestResultRequest
from app.services import test_result_service, user_service

router = APIRouter()

@router.get("/user", response_model=List[TestResultRead])
def get_user_results(user: AuthorizedUser, db: Session = Depends(get_db)):
    """Retrieve all test results for the currently authenticated user."""
    return test_result_service.get_results_for_user(db, user.id)

@router.get("/user/{email}", response_model=List[TestResultRead])
def get_user_results_by_email(email: str, db: Session = Depends(get_db)):
    """Compatibility route: Retrieve all test results for a user by email."""
    user = user_service.get_user_by_email(db, email)
    if not user:
        return []
    return test_result_service.get_results_for_user(db, user.id)

@router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_result(result_id: int, user: AuthorizedUser, db: Session = Depends(get_db)):
    """Delete a test result."""
    result = test_result_service.get_result_by_id(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    if result.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this result")

    test_result_service.delete_result(db, result_id)

@router.post("/testresult", response_model=TestResultRead)
def get_test_result_with_data(request: TestResultRequest, db: Session = Depends(get_db)):
    """Find a specific test result by test ID and user name."""
    result = test_result_service.get_test_result_by_test_and_name(db, test_id=request.test_id, name=request.name)
    if not result:
        raise HTTPException(status_code=404, detail="TestResult not found.")
    return result
