from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.quiz import Part, Section, Question, Option

def get_parts(db: Session, skip: int = 0, limit: int = 100) -> List[Part]:
    return db.query(Part).options(
        joinedload(Part.introduction),
        joinedload(Part.sections).joinedload(Section.questions).joinedload(Question.options)
    ).offset(skip).limit(limit).all()

def get_part_by_id(db: Session, part_id: int) -> Optional[Part]:
    return db.query(Part).options(
        joinedload(Part.introduction),
        joinedload(Part.sections).joinedload(Section.questions).joinedload(Question.options)
    ).filter(Part.part_id == part_id).first()

def get_sections_by_part(db: Session, part_id: int) -> List[Section]:
    return db.query(Section).options(
        joinedload(Section.questions).joinedload(Question.options)
    ).filter(Section.part_id == part_id).all()

def get_section_by_id(db: Session, section_id: int) -> Optional[Section]:
    return db.query(Section).options(
        joinedload(Section.questions).joinedload(Question.options)
    ).filter(Section.section_id == section_id).first()

def get_question_by_id(db: Session, question_id: int) -> Optional[Question]:
    return db.query(Question).options(
        joinedload(Question.options)
    ).filter(Question.question_id == question_id).first()

def get_options_by_question(db: Session, question_id: int) -> List[Option]:
    return db.query(Option).filter(Option.question_id == question_id).all()
