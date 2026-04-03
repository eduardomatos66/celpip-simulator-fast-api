from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, AuthorizedUser
from app.schemas.answer import AnswerSheetCreate, AnswerSheetRead
from app.services import answer_sheet_service

router = APIRouter()

@router.post("/submit",
    response_model=AnswerSheetRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Completed Test",
    description="Submit a full set of answers for a CELPIP test. The server will automatically evaluate multiple-choice questions and store the results for scoring.")
def submit_answer_sheet(
    sheet_in: AnswerSheetCreate,
    user: AuthorizedUser,
    db: Session = Depends(get_db)
):
    try:
        sheet = answer_sheet_service.submit_answer_sheet(db, sheet_in, user.id)
        return sheet
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{sheet_id}",
    response_model=AnswerSheetRead,
    summary="Get Answer Sheet Details",
    description="Retrieve a previously submitted answer sheet by its ID. Access is restricted to the owner of the sheet.",
    responses={403: {"description": "Not authorized to view this sheet"}, 404: {"description": "Answer sheet not found"}})
def get_answer_sheet(sheet_id: int, user: AuthorizedUser, db: Session = Depends(get_db)):
    sheet = answer_sheet_service.get_answer_sheet_by_id(db, sheet_id=sheet_id)
    if not sheet:
        raise HTTPException(status_code=404, detail="Answer sheet not found")

    if sheet.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this sheet")

    return sheet
