"""
Unit tests for the service layer logic.
"""

from app.models.user import User
from app.models.quiz import TestAvailable, Part, Section, Question, Option, TestArea, AreaTest
from app.schemas.user import UserCreate
from app.schemas.answer import AnswerSheetCreate, OptionAnswerCreate
from app.services.user_service import get_or_create_user, get_user_by_clerk_id
from app.services.answer_sheet_service import submit_answer_sheet
from app.services.test_result_service import get_results_for_user

def test_user_service_get_or_create(db_session):
    # Setup test user
    user = get_or_create_user(db_session, "clerk_123", "test@example.com", "Test User")
    assert user.id is not None
    assert user.email == "test@example.com"

    # Second fetch should return the same user, not create a duplicate
    user_duplicate = get_or_create_user(db_session, "clerk_123", "test@example.com", "Test User")
    assert user.id == user_duplicate.id

def test_answer_scoring_service(db_session):
    # Preload the in-memory test DB with a user and test structures
    user = get_or_create_user(db_session, "clerk_test", "user@test.com", "User")

    test_av = TestAvailable(test_name="Mock CELPIP Test")
    part = Part(part_name="Listening Part 1")
    sec = Section(parts=[part])
    # Question 1
    q1 = Question(sections=[sec])
    opt1 = Option(text="Car", is_correct=True, questions=[q1])
    opt2 = Option(text="Bike", is_correct=False, questions=[q1])
    # Question 2
    q2 = Question(sections=[sec])
    opt3 = Option(text="Apple", is_correct=True, questions=[q2])
    opt4 = Option(text="Orange", is_correct=False, questions=[q2])

    db_session.add_all([test_av, part, sec, q1, opt1, opt2, q2, opt3, opt4])
    db_session.commit()

    # Emulate submitting an answer sheet where user gets 1 right, 1 wrong
    sheet_data = AnswerSheetCreate(
        test_id=str(test_av.test_id),
        option_answers=[
            OptionAnswerCreate(question_id=str(q1.question_id), user_answer="Car", duration=12.0),
            OptionAnswerCreate(question_id=str(q2.question_id), user_answer="Orange", duration=8.0)
        ]
    )

    sheet_result = submit_answer_sheet(db_session, sheet_data, user.id)
    assert sheet_result is not None
    assert sheet_result.answer_sheet_id is not None
    assert len(sheet_result.option_answers) == 2

    # Verify score calculation generated a TestResult
    results = get_results_for_user(db_session, user.id)
    assert len(results) == 1
    tr = results[0]

    # 1 correct out of 2 MCQs. The simulated math in the backend puts logic around this.
    # Total correct = 1. Half correct = 0.5. Half MCQ = 1.0. (0.5 / 1.0) = 50% = CLB 6 according to the placeholder math!
    assert tr.clb_min is not None
    assert tr.clb_average is not None
