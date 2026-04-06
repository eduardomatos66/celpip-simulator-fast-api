from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.models.answer import TestResult, AnswerSheet, OptionAnswer
from app.core.decorators import log_execution_time

@log_execution_time
def get_results_for_user(db: Session, user_id: int) -> List[TestResult]:
    return db.query(TestResult).filter(TestResult.user_id == user_id).options(
        joinedload(TestResult.test_available)
    ).all()

@log_execution_time
def get_result_by_id(db: Session, result_id: int) -> Optional[TestResult]:
    return db.query(TestResult).filter(TestResult.test_result_id == result_id).options(
        joinedload(TestResult.test_available)
    ).first()

@log_execution_time
def get_result_details(db: Session, result_id: int) -> Optional[TestResult]:
    result = db.query(TestResult).filter(TestResult.test_result_id == result_id).options(
        joinedload(TestResult.test_available),
        joinedload(TestResult.answer_sheet).joinedload(AnswerSheet.option_answers)
    ).first()

    return result

@log_execution_time
def delete_result(db: Session, result_id: int) -> bool:
    res = get_result_by_id(db, result_id)
    if res:
        db.delete(res)
        db.commit()
        return True
    return False

def _compute_clb_listening_reading(score: int, max_score: float) -> int:
    """
    Placeholder logic for CELPIP CLB Band mapping.
    This should be accurately mapped according to the real CELPIP simulator scoring matrix.
    """
    if max_score <= 0: return 0
    percent = score / max_score
    if percent >= 0.9: return 10
    if percent >= 0.8: return 9
    if percent >= 0.7: return 8
    if percent >= 0.6: return 7
    if percent >= 0.5: return 6
    if percent >= 0.4: return 5
    if percent >= 0.3: return 4
    return 3

@log_execution_time
def calculate_exam_score(db: Session, answer_sheet_id: int, test_id: str, user_id: int) -> Optional[TestResult]:
    """
    Internal logic to auto-score multiple choice questions (Listening/Reading).
    Speaking & Writing are returned with defaults (usually manually graded later).
    """
    sheet = db.query(AnswerSheet).filter(AnswerSheet.answer_sheet_id == answer_sheet_id).first()
    if not sheet:
        return None

    # We don't have the exact complex matching currently, so we simulate exact string matches
    # for Listening/Reading, matching `user_answer` vs `correct_answer`.
    # Assuming half queries go to LISTENING, half to READING based on Part ID,
    # but currently we just evaluate overall correctness for simplicity in the skeleton.

    correct_count = 0
    total_mcq = 0

    for opts in sheet.option_answers:
        if opts.correct_answer:  # It is an MCQ
            total_mcq += 1
            if opts.user_answer and str(opts.user_answer).strip().lower() == str(opts.correct_answer).strip().lower():
                correct_count += 1

    # Simple half/half split simulation for the skeleton structure
    half_mcq = total_mcq / 2.0 if total_mcq > 0 else 1.0
    half_correct = correct_count / 2.0

    clb_L = _compute_clb_listening_reading(int(half_correct), half_mcq)
    clb_R = _compute_clb_listening_reading(int(half_correct), half_mcq)

    # Defaults for Writing/Speaking if empty
    w_min, w_max = 6.0, 8.0
    s_min, s_max = 6.0, 8.0

    clb_avg = (clb_L + clb_R + ((w_min+w_max)/2) + ((s_min+s_max)/2)) / 4.0

    result = TestResult(
        user_id=user_id,
        answer_sheet_id=answer_sheet_id,
        available_test_id=int(test_id) if test_id.isdigit() else None,
        listening_corrects=int(half_correct),
        listening_max=half_mcq,
        reading_corrects=int(half_correct),
        reading_max=half_mcq,
        writing_min=w_min,
        writing_max=w_max,
        speaking_min=s_min,
        speaking_max=s_max,
        clb_min=min([clb_L, clb_R, w_min, s_min]),
        clb_max=max([clb_L, clb_R, w_max, s_max]),
        clb_average=clb_avg
    )

    db.add(result)
    db.commit()
    db.refresh(result)
    return result

@log_execution_time
def get_test_result_by_test_and_name(db: Session, test_id: int, name: str) -> Optional[TestResult]:
    from app.models.user import User
    return db.query(TestResult).join(User, TestResult.user_id == User.id).filter(
        TestResult.available_test_id == test_id,
        (User.full_name == name) | (User.email == name)
    ).first()
