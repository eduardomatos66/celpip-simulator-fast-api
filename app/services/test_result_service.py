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

import re

def _clean_text(text: Optional[str]) -> str:
    """Helper to strip HTML tags and normalize whitespace for comparison."""
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    # Normalize whitespace and lowercase
    return " ".join(clean.split()).lower()

@log_execution_time
def calculate_exam_score(db: Session, answer_sheet_id: int, test_id: str, user_id: int) -> Optional[TestResult]:
    """
    Internal logic to auto-score multiple choice questions (Listening/Reading).
    Identifies the area (Listening/Reading) for each question to provide accurate sub-scores.
    """
    from app.models.quiz import Question, Section, Part, TestArea

    sheet = db.query(AnswerSheet).options(
        joinedload(AnswerSheet.option_answers)
    ).filter(AnswerSheet.answer_sheet_id == answer_sheet_id).first()

    if not sheet:
        return None

    scores = {
        "listening": {"correct": 0, "total": 0},
        "reading": {"correct": 0, "total": 0}
    }

    for opt_ans in sheet.option_answers:
        if not opt_ans.correct_answer:
            continue

        # Determine current question's area
        area_name = "reading" # Default fallback
        try:
            q_id = int(opt_ans.question_id) if str(opt_ans.question_id).isdigit() else None
            if q_id:
                # Trace: Question -> Section -> Part -> TestArea
                area_obj = db.query(TestArea).join(TestArea.parts).join(Part.sections).join(Section.questions).filter(Question.question_id == q_id).first()
                if area_obj:
                    area_name = area_obj.area_name.lower()
        except Exception:
            pass

        if area_name not in scores:
            continue

        scores[area_name]["total"] += 1

        user_clean = _clean_text(opt_ans.user_answer)
        corr_clean = _clean_text(opt_ans.correct_answer)

        if user_clean and user_clean == corr_clean:
            scores[area_name]["correct"] += 1

    clb_L = _compute_clb_listening_reading(scores["listening"]["correct"], scores["listening"]["total"])
    clb_R = _compute_clb_listening_reading(scores["reading"]["correct"], scores["reading"]["total"])

    # Defaults for Writing/Speaking (manually graded)
    w_min, w_max = 0.0, 0.0
    s_min, s_max = 0.0, 0.0

    clb_avg = (clb_L + clb_R + 0 + 0) / 4.0 # Simplified average for placeholder

    result = TestResult(
        user_id=user_id,
        answer_sheet_id=answer_sheet_id,
        available_test_id=int(test_id) if test_id.isdigit() else None,
        listening_corrects=scores["listening"]["correct"],
        listening_max=float(scores["listening"]["total"]),
        reading_corrects=scores["reading"]["correct"],
        reading_max=float(scores["reading"]["total"]),
        writing_min=w_min,
        writing_max=w_max,
        speaking_min=s_min,
        speaking_max=s_max,
        clb_min=float(min([clb_L, clb_R])),
        clb_max=float(max([clb_L, clb_R])),
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
