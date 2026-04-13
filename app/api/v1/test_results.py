from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, AuthorizedUser, EditorUser
from app.schemas.answer import TestResultRead, TestResultRequest, TestResultDetail
from app.services import test_result_service, user_service

router = APIRouter()

@router.get("/user",
    response_model=List[TestResultRead],
    summary="Get My Test Results",
    description="Retrieve a historical list of all completed test results for the currently authenticated user. Includes skill-based scores and CLB levels.")
def get_user_results(user: AuthorizedUser, db: Session = Depends(get_db)):
    results = test_result_service.get_results_for_user(db, user.id)
    return results

@router.get("/{result_id}",
    response_model=TestResultDetail,
    summary="Get Test Result Details",
    description="Retrieve full details for a specific test result, including answers.")
def get_test_result_details(result_id: int, user: AuthorizedUser, db: Session = Depends(get_db)):
    result = test_result_service.get_result_details(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    if result.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this result")
    return result

@router.get("/user/{email}",
    response_model=List[TestResultRead],
    summary="Get Test Results by Email",
    description="Retrieve all test results associated with a specific user email. Mainly for compatibility with legacy components and admin lookup.")
def get_user_results_by_email(email: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(db, email)
    if not user:
        return []
    return test_result_service.get_results_for_user(db, user.id)

@router.delete("/{result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Test Result",
    description="Permanently remove a test result from the user's history. Access is restricted to the owner of the result.",
    responses={403: {"description": "Not authorized to delete this result"}, 404: {"description": "Result not found"}})
def delete_test_result(result_id: int, user: EditorUser, db: Session = Depends(get_db)):
    result = test_result_service.get_result_by_id(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    if result.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this result")

    test_result_service.delete_result(db, result_id)

@router.post("/testresult",
    response_model=TestResultRead,
    summary="Search Result by Test and Name",
    description="Find a specific test result using the combination of test ID and the user's registered name. Used for quick lookup without session-based ownership checks in specific workflows.")
def get_test_result_with_data(request: TestResultRequest, db: Session = Depends(get_db)):
    result = test_result_service.get_test_result_by_test_and_name(db, test_id=request.test_id, name=request.name)
    if not result:
        raise HTTPException(status_code=404, detail="TestResult not found.")
    return result
