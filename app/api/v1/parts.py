from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.quiz import PartRead, SectionRead
from app.services import quiz_service

router = APIRouter()

@router.get("/", response_model=List[PartRead])
def get_parts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all parts with their sections, questions, and options."""
    parts = quiz_service.get_parts(db, skip=skip, limit=limit)
    return parts

@router.get("/{part_id}", response_model=PartRead)
def get_part(part_id: int, db: Session = Depends(get_db)):
    """Get a specific part by ID."""
    part = quiz_service.get_part_by_id(db, part_id=part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part

@router.get("/{part_id}/sections", response_model=List[SectionRead])
def get_sections_for_part(part_id: int, db: Session = Depends(get_db)):
    """Get all sections belonging to a specific part."""
    sections = quiz_service.get_sections_by_part(db, part_id=part_id)
    return sections
