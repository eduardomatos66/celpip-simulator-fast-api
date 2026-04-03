from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.quiz import PartRead, SectionRead, PartCreate, PartUpdate
from app.services import quiz_service

router = APIRouter()

@router.get("",
    response_model=List[PartRead],
    summary="List All Parts",
    description="Retrieve a paginated list of all test parts, including their nested sections and questions.")
def get_parts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    parts = quiz_service.get_parts(db, skip=skip, limit=limit)
    return parts

@router.get("/{part_id}",
    response_model=PartRead,
    summary="Get Part Details",
    description="Retrieve a specific part by its ID, with all nested content.")
def get_part(part_id: int, db: Session = Depends(get_db)):
    part = quiz_service.get_part_by_id(db, part_id=part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part

@router.get("/{part_id}/sections",
    response_model=List[SectionRead],
    summary="Get Sections for Part",
    description="Retrieve all sections that belong to a specific test part.")
def get_sections_for_part(part_id: int, db: Session = Depends(get_db)):
    sections = quiz_service.get_sections_by_part(db, part_id=part_id)
    return sections

@router.post("",
    response_model=PartRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Part",
    description="Create a new test part record (Listening, Reading, etc.).")
def create_part(part_in: PartCreate, db: Session = Depends(get_db)):
    return quiz_service.create_part(db, part_in)

@router.put("/{part_id}",
    response_model=PartRead,
    summary="Update Part",
    description="Modify an existing part's details.")
def update_part(part_id: int, part_in: PartUpdate, db: Session = Depends(get_db)):
    db_obj = quiz_service.get_part_by_id(db, part_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail=f"Part {part_id} not found")
    return quiz_service.update_part(db, db_obj, part_in)

@router.delete("/{part_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Part",
    description="Permanently delete a part from the system.")
def delete_part(part_id: int, db: Session = Depends(get_db)):
    success = quiz_service.delete_part(db, part_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Part {part_id} not found")
    return None
