from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.quiz import TestAvailable, TestArea, Part, Section, Question, Option, AreaTest

def get_test_available_by_id(db: Session, test_id: int) -> Optional[TestAvailable]:
    """Retrieve a specific test with its full hierarchy."""
    return db.query(TestAvailable).options(
        joinedload(TestAvailable.test_areas).joinedload(TestArea.part).joinedload(Part.introduction),
        joinedload(TestAvailable.test_areas).joinedload(TestArea.part).joinedload(Part.sections).joinedload(Section.questions).joinedload(Question.options)
    ).filter(TestAvailable.test_id == test_id).first()

def get_tests_summary(db: Session) -> List[TestAvailable]:
    """Retrieve a summary list of tests without deep eager loading."""
    return db.query(TestAvailable).options(
        joinedload(TestAvailable.test_areas)
    ).all()
