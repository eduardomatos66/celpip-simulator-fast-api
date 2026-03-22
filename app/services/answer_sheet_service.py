from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.answer import AnswerSheet, OptionAnswer
from app.schemas.answer import AnswerSheetCreate
from app.services.quiz_service import get_options_by_question
from app.services.test_result_service import calculate_exam_score

def get_answer_sheet_by_id(db: Session, sheet_id: int) -> Optional[AnswerSheet]:
    return db.query(AnswerSheet).options(
        joinedload(AnswerSheet.option_answers)
    ).filter(AnswerSheet.answer_sheet_id == sheet_id).first()

def get_answer_sheets_for_user(db: Session, user_id: int) -> List[AnswerSheet]:
    return db.query(AnswerSheet).filter(AnswerSheet.user_id == user_id).all()

def submit_answer_sheet(db: Session, sheet_in: AnswerSheetCreate, user_id: int) -> AnswerSheet:
    """
    Submits an answer sheet.
    For each user answer, we identify the correct answer text directly from the quiz options
    to store it in OptionAnswer.correct_answer.
    Then we compute the TestResult logic.
    """
    db_sheet = AnswerSheet(
        test_id=sheet_in.test_id,
        user_id=user_id,
    )
    db.add(db_sheet)
    db.flush() # flush to get ID

    for ans in sheet_in.option_answers:
        # Resolve correct answer
        question_id = int(ans.question_id) if ans.question_id.isdigit() else None
        
        correct_text = None
        if question_id:
            options = get_options_by_question(db, question_id)
            correct_opt = next((opt for opt in options if opt.is_correct), None)
            if correct_opt:
                correct_text = correct_opt.text
                
        db_opt_answer = OptionAnswer(
            answer_sheet_id=db_sheet.answer_sheet_id,
            question_id=ans.question_id,
            user_answer=ans.user_answer,
            correct_answer=correct_text,
            duration=ans.duration
        )
        db.add(db_opt_answer)

    db.commit()
    db.refresh(db_sheet)

    # Trigger async/sync scoring logic
    calculate_exam_score(db, db_sheet.answer_sheet_id, db_sheet.test_id, user_id)

    return db_sheet
