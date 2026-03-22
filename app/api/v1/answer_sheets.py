from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, CurrentUserClaims
from app.schemas.answer import AnswerSheetCreate, AnswerSheetRead
from app.services import answer_sheet_service, user_service

router = APIRouter()

@router.post("/submit", response_model=AnswerSheetRead, status_code=status.HTTP_201_CREATED)
def submit_answer_sheet(
    sheet_in: AnswerSheetCreate,
    claims: CurrentUserClaims,
    db: Session = Depends(get_db)
):
    """Submit an answer sheet and compute the test score."""
    clerk_id = claims.get("sub")
    email = claims.get("email", "")
    name = claims.get("name", "")
    
    user = user_service.get_or_create_user(db, clerk_id, email, name)
    try:
        sheet = answer_sheet_service.submit_answer_sheet(db, sheet_in, user.user_id)
        return sheet
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{sheet_id}", response_model=AnswerSheetRead)
def get_answer_sheet(sheet_id: int, claims: CurrentUserClaims, db: Session = Depends(get_db)):
    """Retrieve an answer sheet."""
    # Authenticated endpoint
    sheet = answer_sheet_service.get_answer_sheet_by_id(db, sheet_id=sheet_id)
    if not sheet:
        raise HTTPException(status_code=404, detail="Answer sheet not found")
        
    user = user_service.get_or_create_user(db, claims["sub"], claims.get("email",""), "")
    if sheet.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this sheet")
        
    return sheet
