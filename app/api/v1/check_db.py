from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.services import dbchecking_service

router = APIRouter()

@router.get("/check-orphans")
def check_orphans(db: Session = Depends(get_db)):
    """Deletes orphaned entities in the database."""
    return dbchecking_service.check_orphan_entities(db)

@router.get("/check-non-valid-questions")
def check_non_valid_questions(db: Session = Depends(get_db)):
    """Finds questions with no correct option designated."""
    return dbchecking_service.check_non_valid_questions(db)

@router.get("/check-links")
async def check_links(db: Session = Depends(get_db)):
    """Verifies media URL accessibility for options, questions, and sections."""
    return await dbchecking_service.check_links(db)
