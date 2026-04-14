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
    Standard CELPIP-aligned CLB Band mapping.
    Based on ~38 question format with score equating.
    """
    if max_score <= 0: return 0
    percent = score / max_score

    if percent >= 0.92: return 10
    if percent >= 0.86: return 9
    if percent >= 0.78: return 8
    if percent >= 0.71: return 7
    if percent >= 0.58: return 6
    if percent >= 0.44: return 5
    if percent >= 0.29: return 4
    return 3 if score > 0 else 0

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
    # 1. Fetch the test structure once to build an area map
    from app.models.quiz import TestAvailable, TestArea, Part, Section, Question

    t_id_int = int(test_id) if test_id.isdigit() else None
    area_map = {}

    if t_id_int:
        # Get test with all areas, parts, sections, questions
        test_struct = db.query(TestAvailable).filter(TestAvailable.test_id == t_id_int).options(
            joinedload(TestAvailable.test_areas)
            .joinedload(TestArea.parts)
            .joinedload(Part.sections)
            .joinedload(Section.questions)
        ).first()

        if test_struct:
            for area in test_struct.test_areas:
                a_name = area.area_name.lower()
                for part in area.parts:
                    for section in part.sections:
                        for q in section.questions:
                            area_map[str(q.question_id)] = a_name

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
        area_name = None
        q_raw = str(opt_ans.question_id).strip()

        # Priority 1: Use the pre-calculated map from DB hierarchy
        if q_raw in area_map:
            area_name = area_map[q_raw]
        else:
            # Priority 2: Fallback to token extraction (e.g. t1-LISTENING-p1-s1-q1)
            token_match = re.search(r"-([a-zA-Z]+)-p", q_raw, re.IGNORECASE)
            if token_match:
                area_name = token_match.group(1).lower()

        if not area_name or area_name not in scores:
            continue

        scores[area_name]["total"] += 1

        user_clean = _clean_text(opt_ans.user_answer)
        corr_clean = _clean_text(opt_ans.correct_answer)

        if user_clean and user_clean == corr_clean:
            scores[area_name]["correct"] += 1

    clb_L = _compute_clb_listening_reading(scores["listening"]["correct"], scores["listening"]["total"])
    clb_R = _compute_clb_listening_reading(scores["reading"]["correct"], scores["reading"]["total"])

    # Defaults for Writing/Speaking (manually graded placeholders)
    # In a full practice test, these are typically handled by human or AI evaluation
    clb_W = 0
    clb_S = 0

    # Calculate average based only on completed sections
    active_scores = []
    if scores["listening"]["total"] > 0: active_scores.append(clb_L)
    if scores["reading"]["total"] > 0: active_scores.append(clb_R)

    clb_avg = sum(active_scores) / len(active_scores) if active_scores else 0.0

    result = TestResult(
        user_id=user_id,
        answer_sheet_id=answer_sheet_id,
        available_test_id=int(test_id) if test_id.isdigit() else None,
        listening_corrects=scores["listening"]["correct"],
        listening_max=float(scores["listening"]["total"]),
        reading_corrects=scores["reading"]["correct"],
        reading_max=float(scores["reading"]["total"]),
        writing_min=0.0,
        writing_max=0.0,
        speaking_min=0.0,
        speaking_max=0.0,
        clb_min=float(min(active_scores)) if active_scores else 0.0,
        clb_max=float(max(active_scores)) if active_scores else 0.0,
        clb_average=round(clb_avg, 2)
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
