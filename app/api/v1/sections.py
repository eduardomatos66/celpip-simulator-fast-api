from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.quiz import SectionRead
from app.services import quiz_service

router = APIRouter()

@router.get("/{section_id}", response_model=SectionRead)
def get_section(section_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific section."""
    section = quiz_service.get_section_by_id(db, section_id=section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section
