from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, CurrentUserClaims
from app.schemas.answer import TestResultRead
from app.services import test_result_service, user_service

router = APIRouter()

@router.get("/user", response_model=List[TestResultRead])
def get_user_results(claims: CurrentUserClaims, db: Session = Depends(get_db)):
    """Retrieve all test results for the currently authenticated user."""
    clerk_id = claims.get("sub")
    user = user_service.get_user_by_clerk_id(db, clerk_id)
    if not user:
        return []
    
    return test_result_service.get_results_for_user(db, user.user_id)

@router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_result(result_id: int, claims: CurrentUserClaims, db: Session = Depends(get_db)):
    """Delete a test result."""
    result = test_result_service.get_result_by_id(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
        
    user = user_service.get_user_by_clerk_id(db, claims["sub"])
    if not user or result.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this result")
        
    test_result_service.delete_result(db, result_id)
