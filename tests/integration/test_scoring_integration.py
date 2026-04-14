import pytest
from app.services.answer_sheet_service import submit_answer_sheet
from app.services.test_result_service import get_results_for_user
from app.services.user_service import get_or_create_user
from app.models.quiz import TestAvailable, TestArea, Part, Section, Question, Option, AreaTest
from app.schemas.answer import AnswerSheetCreate, OptionAnswerCreate

def test_composite_token_scoring_flow(db_session):
    # 1. Setup Test Structure
    user = get_or_create_user(db_session, "clerk_token_test", "token@test.com", "Token User")

    test_av = TestAvailable(test_name="Integration Test 001")
    db_session.add(test_av)
    db_session.flush()
    test_id = test_av.test_id

    # Create Listening Area
    area_L = TestArea(area_name="LISTENING")
    db_session.add(area_L)
    test_av.test_areas.append(area_L)

    part_L = Part(part_name="Listening Part 1", part_number=1)
    db_session.add(part_L)
    area_L.parts.append(part_L)

    sec_L = Section(section_number=1)
    db_session.add(sec_L)
    part_L.sections.append(sec_L)

    q_L = Question(question_number=1)
    db_session.add(q_L)
    sec_L.questions.append(q_L)

    opt_L = Option(text="Correct L", is_correct=True)
    q_L.options.append(opt_L)

    # Create Reading Area
    area_R = TestArea(area_name="READING")
    db_session.add(area_R)
    test_av.test_areas.append(area_R)

    part_R = Part(part_name="Reading Part 1", part_number=1)
    db_session.add(part_R)
    area_R.parts.append(part_R)

    sec_R = Section(section_number=1)
    db_session.add(sec_R)
    part_R.sections.append(sec_R)

    q_R = Question(question_number=1)
    db_session.add(q_R)
    sec_R.questions.append(q_R)

    opt_R = Option(text="Correct R", is_correct=True)
    q_R.options.append(opt_R)

    db_session.commit()

    # 2. Submit Answers using Composite Tokens
    # Format: t{test_id}-{area_name}-p{part_num}-s{sec_num}-q{q_num}
    token_L = f"t{test_id}-LISTENING-p1-s1-q1"
    token_R = f"t{test_id}-READING-p1-s1-q1"

    sheet_data = AnswerSheetCreate(
        test_id=str(test_id),
        option_answers=[
            OptionAnswerCreate(question_id=token_L, user_answer="Correct L"),
            OptionAnswerCreate(question_id=token_R, user_answer="Correct R")
        ]
    )

    submit_answer_sheet(db_session, sheet_data, user.id)

    # 3. Verify Result
    results = get_results_for_user(db_session, user.id)
    assert len(results) == 1
    tr = results[0]

    # Check Separation
    assert tr.listening_max == 1.0
    assert tr.listening_corrects == 1
    assert tr.reading_max == 1.0
    assert tr.reading_corrects == 1

    # Check Calculus
    # Since 1/1 = 100%, CLB should be 10
    assert tr.clb_min == 10.0
    assert tr.clb_max == 10.0
    assert tr.clb_average == 10.0
