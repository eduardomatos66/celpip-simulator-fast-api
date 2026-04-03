from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.quiz import TestAreaRead, TestAreaCreate, TestAreaUpdate
from app.services import test_area_service

router = APIRouter()

@router.get("",
    response_model=List[TestAreaRead],
    summary="List All Test Areas",
    description="Retrieve all test area records (Listening, Reading, Writing, Speaking).")
def get_all_test_areas(db: Session = Depends(get_db)):
    return test_area_service.get_test_areas(db)

@router.get("/{id}",
    response_model=TestAreaRead,
    summary="Get Test Area Details",
    description="Retrieve a specific test area by its ID.")
def get_test_area_by_id(id: int, db: Session = Depends(get_db)):
    test_area = test_area_service.get_test_area_by_id(db, id)
    if not test_area:
        raise HTTPException(status_code=404, detail=f"TestArea {id} not found")
    return test_area

@router.post("",
    response_model=TestAreaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Test Area",
    description="Create a new test area record.")
def create_test_area(test_area_in: TestAreaCreate, db: Session = Depends(get_db)):
    return test_area_service.create_test_area(db, test_area_in)

@router.put("/{id}",
    response_model=TestAreaRead,
    summary="Update Test Area",
    description="Modify an existing test area record.")
def update_test_area(id: int, test_area_in: TestAreaUpdate, db: Session = Depends(get_db)):
    db_obj = test_area_service.get_test_area_by_id(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail=f"TestArea {id} not found")
    return test_area_service.update_test_area(db, db_obj, test_area_in)

@router.delete("/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Test Area",
    description="Permanently remove a test area record.")
def delete_test_area(id: int, db: Session = Depends(get_db)):
    success = test_area_service.delete_test_area(db, id)
    if not success:
        raise HTTPException(status_code=404, detail=f"TestArea {id} not found")
    return None
