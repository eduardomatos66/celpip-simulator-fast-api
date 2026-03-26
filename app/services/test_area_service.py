from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.quiz import TestArea
from app.schemas.quiz import TestAreaCreate, TestAreaUpdate
from app.core.decorators import log_execution_time

@log_execution_time
def get_test_areas(db: Session) -> List[TestArea]:
    return db.query(TestArea).all()

@log_execution_time
def get_test_area_by_id(db: Session, test_area_id: int) -> Optional[TestArea]:
    return db.query(TestArea).filter(TestArea.test_area_id == test_area_id).first()

@log_execution_time
def create_test_area(db: Session, test_area_in: TestAreaCreate) -> TestArea:
    db_obj = TestArea(**test_area_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@log_execution_time
def update_test_area(db: Session, db_obj: TestArea, test_area_in: TestAreaUpdate) -> TestArea:
    update_data = test_area_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@log_execution_time
def delete_test_area(db: Session, test_area_id: int) -> bool:
    obj = db.query(TestArea).filter(TestArea.test_area_id == test_area_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
