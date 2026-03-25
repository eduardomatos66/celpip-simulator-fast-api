from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.quiz import Part, Section, Question, Option
from app.schemas.quiz import PartCreate, PartUpdate, SectionCreate, SectionUpdate

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

def create_part(db: Session, part_in: "PartCreate") -> Part:
    db_obj = Part(**part_in.model_dump(exclude={"sections", "introduction"}))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_part(db: Session, db_obj: Part, part_in: "PartUpdate") -> Part:
    obj_data = db_obj.__dict__
    update_data = part_in.model_dump(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_part(db: Session, part_id: int) -> bool:
    part = get_part_by_id(db, part_id)
    if part:
        db.delete(part)
        db.commit()
        return True
    return False

def get_sections(db: Session, skip: int = 0, limit: int = 100) -> List[Section]:
    return db.query(Section).options(
        joinedload(Section.questions).joinedload(Question.options)
    ).offset(skip).limit(limit).all()

def create_section(db: Session, section_in: "SectionCreate") -> Section:
    db_obj = Section(**section_in.model_dump(exclude={"questions"}))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_section(db: Session, db_obj: Section, section_in: "SectionUpdate") -> Section:
    obj_data = db_obj.__dict__
    update_data = section_in.model_dump(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_section(db: Session, section_id: int) -> bool:
    section = get_section_by_id(db, section_id)
    if section:
        db.delete(section)
        db.commit()
        return True
    return False
