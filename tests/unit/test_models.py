"""
Tests for SQLAlchemy models to ensure relations, columns, and constraints are valid.
"""

from app.models.user import User
from app.models.quiz import TestAvailable, TestArea, AreaTest, Part, Section, Question, Option, PartIntroduction
from app.models.answer import AnswerSheet, OptionAnswer, TestResult

def test_user_model_creation(db_session):
    user = User(full_name="Test User", email="test@example.com", clerk_id="user_2abc123")
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.full_name == "Test User"
    assert user.created_at is not None

def test_quiz_hierarchy_creation(db_session):
    # Create the top level test
    test = TestAvailable(test_name="CELPIP General Practice 1")
    
    # Create introduction
    intro = PartIntroduction(text="Welcome to the test", auxiliary_texts="Instructions here")
    
    # Create part
    part = Part(part_number=1, part_name="Part 1: Listening to Problem Solving", time=100, introduction=intro)
    
    # Create section
    section = Section(section_number=1, time=60, text="Read the following...", part=part)
    
    # Create question and options
    question = Question(question_number=1, text="What is the main topic?", time=30, section=section)
    option_1 = Option(text="Topic A", is_correct=True, question=question)
    option_2 = Option(text="Topic B", is_correct=False, question=question)
    
    # Area Test linkage
    test_area = TestArea(area=AreaTest.LISTENING, test_available=test, part=part)
    
    db_session.add_all([test, test_area, intro, part, section, question, option_1, option_2])
    db_session.commit()
    
    assert test.test_id is not None
    assert len(test.test_areas) == 1
    assert test.test_areas[0].area == AreaTest.LISTENING
    assert test_area.part.part_name == "Part 1: Listening to Problem Solving"
    assert len(test_area.part.sections) == 1
    assert len(section.questions) == 1
    assert len(question.options) == 2

def test_answer_model_creation(db_session):
    user = User(full_name="Answer User", email="answer@example.com", clerk_id="user_ans123")
    test = TestAvailable(test_name="CELPIP Test 2")
    
    sheet = AnswerSheet(user=user, test_id="2")
    opt_answer = OptionAnswer(question_id="101", user_answer="Topic A", correct_answer="Topic A", duration=15.5, answer_sheet=sheet)
    
    result = TestResult(
        user=user,
        test_available=test,
        listening_corrects=30, listening_max=38,
        reading_corrects=28, reading_max=38,
        writing_min=7.0, writing_max=8.0,
        speaking_min=8.0, speaking_max=9.0,
        clb_min=7.0, clb_max=8.0, clb_average=7.5
    )
    
    db_session.add_all([user, test, sheet, opt_answer, result])
    db_session.commit()
    
    assert sheet.answer_sheet_id is not None
    assert sheet.user_id == user.id
    assert len(sheet.option_answers) == 1
    assert result.test_result_id is not None
    assert result.clb_average == 7.5
