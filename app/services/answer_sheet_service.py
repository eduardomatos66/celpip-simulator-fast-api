import re
import logging
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.answer import AnswerSheet, OptionAnswer
from app.models.quiz import TestAvailable, TestArea, Part, Section, Question
from app.schemas.answer import AnswerSheetCreate
from app.services.quiz_service import get_options_by_question
from app.services.test_result_service import calculate_exam_score
from app.core.decorators import log_execution_time

logger = logging.getLogger(__name__)

def _resolve_question_pk(db: Session, logical_id: str) -> Optional[int]:
    """
    Resolves a logical ID like 't1-listening-p1-s1-q1' to a numeric question_id.
    Pattern: t{test_id}-{area}-p{part_num}-s{section_num}-q{question_num}
    """
    from app.models.quiz import (
        test_available_test_areas, test_area_parts, part_sections, section_questions
    )

    pattern = r"t(\d+)-([a-zA-Z]+)-p(\d+)-s(\d+)-q(\d+)"
    match = re.match(pattern, logical_id, re.IGNORECASE)
    if not match:
        return None

    t_id, a_name, p_num, s_num, q_num = match.groups()

    try:
        # Use explicit joins on junction tables to be super-robust against ORM mismatches
        query = (
            db.query(Question.question_id)
            .join(section_questions, Question.question_id == section_questions.c.questions_question_id)
            .join(Section, Section.section_id == section_questions.c.section_section_id)
            .join(part_sections, Section.section_id == part_sections.c.sections_section_id)
            .join(Part, Part.part_id == part_sections.c.part_part_id)
            .join(test_area_parts, Part.part_id == test_area_parts.c.parts_part_id)
            .join(TestArea, TestArea.test_area_id == test_area_parts.c.test_area_area_id)
            .join(test_available_test_areas, TestArea.test_area_id == test_available_test_areas.c.test_areas_area_id)
            .join(TestAvailable, TestAvailable.test_id == test_available_test_areas.c.test_available_available_test_id)
            .filter(
                TestAvailable.test_id == int(t_id),
                # We handle the area Name case loosely
                (TestArea.area_name.ilike(a_name)) | (TestArea.area_name.ilike(f"%{a_name}%")),
                Part.part_number == int(p_num),
                Section.section_number == int(s_num),
                Question.question_number == int(q_num)
            )
        )
        result = query.first()
        if result:
            return result[0]
    except Exception as e:
        logger.error(f"Error resolving logical question ID {logical_id}: {e}")

    return None

@log_execution_time
def get_answer_sheet_by_id(db: Session, sheet_id: int) -> Optional[AnswerSheet]:
    return db.query(AnswerSheet).options(
        joinedload(AnswerSheet.option_answers)
    ).filter(AnswerSheet.answer_sheet_id == sheet_id).first()

@log_execution_time
def get_answer_sheets_for_user(db: Session, user_id: int) -> List[AnswerSheet]:
    return db.query(AnswerSheet).filter(AnswerSheet.user_id == user_id).all()

@log_execution_time
def submit_answer_sheet(db: Session, sheet_in: AnswerSheetCreate, user_id: int) -> AnswerSheet:
    """
    Submits an answer sheet.
    Resolves question_id (can be numeric or logical string) to retrieve the correct answer and score.
    """
    db_sheet = AnswerSheet(
        test_id=sheet_in.test_id,
        user_id=user_id,
        start_time=sheet_in.start_time,
        end_time=sheet_in.end_time,
    )
    db.add(db_sheet)
    db.flush()

    for ans in sheet_in.option_answers:
        q_raw = str(ans.question_id).strip()

        # 1. Try numeric resolution first
        question_id_int = int(q_raw) if q_raw.isdigit() else None

        # 2. Try logical resolution if not numeric
        if not question_id_int:
            question_id_int = _resolve_question_pk(db, q_raw)

        correct_text = None
        user_res_text = ans.user_answer

        if question_id_int:
            options = get_options_by_question(db, question_id_int)

            # Resolve Correct Answer Text
            correct_opt = next((opt for opt in options if opt.is_correct), None)
            if correct_opt:
                correct_text = correct_opt.text

            # Resolve User Answer if it's an ID
            u_ans_raw = str(ans.user_answer).strip()
            if u_ans_raw.isdigit():
                u_opt_id = int(u_ans_raw)
                user_opt = next((opt for opt in options if opt.option_id == u_opt_id), None)
                if user_opt:
                    user_res_text = user_opt.text

        db_opt_answer = OptionAnswer(
            answer_sheet_id=db_sheet.answer_sheet_id,
            question_id=ans.question_id,
            user_answer=user_res_text,
            correct_answer=correct_text,
            duration=ans.duration
        )
        db.add(db_opt_answer)

    db.commit()
    db.refresh(db_sheet)

    calculate_exam_score(db, db_sheet.answer_sheet_id, db_sheet.test_id, user_id)
    return db_sheet
