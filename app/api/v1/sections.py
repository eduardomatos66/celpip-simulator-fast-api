from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.quiz import SectionRead, SectionCreate, SectionUpdate
from app.services import quiz_service
from typing import List

router = APIRouter()

@router.get("/{section_id}", response_model=SectionRead)
def get_section(section_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific section."""
    section = quiz_service.get_section_by_id(db, section_id=section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section

@router.get("", response_model=List[SectionRead])
def get_all_sections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all sections."""
    return quiz_service.get_sections(db, skip=skip, limit=limit)

@router.post("", response_model=SectionRead, status_code=status.HTTP_201_CREATED)
def create_section(section_in: SectionCreate, db: Session = Depends(get_db)):
    """Create a new Section."""
    return quiz_service.create_section(db, section_in)

@router.put("/{section_id}", response_model=SectionRead)
def update_section(section_id: int, section_in: SectionUpdate, db: Session = Depends(get_db)):
    """Update an existing Section."""
    db_obj = quiz_service.get_section_by_id(db, section_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail=f"Section {section_id} not found")
    return quiz_service.update_section(db, db_obj, section_in)

@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(section_id: int, db: Session = Depends(get_db)):
    """Delete a Section."""
    success = quiz_service.delete_section(db, section_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Section {section_id} not found")
    return None
