import pytest
from app.services import quiz_service
from app.models.quiz import Part, Section, Question, Option, PartIntroduction

def test_quiz_service_methods(db_session):
    # Setup dummy data for testing the foreign keys correctly
    intro = PartIntroduction(text="Intro Text", auxiliary_texts="Aux Text")
    db_session.add(intro)
    db_session.flush()

    part = Part(part_number=1, part_name="Test Part", introduction_id=intro.part_introduction_id)
    db_session.add(part)
    db_session.flush()

    section = Section(section_number=1, text="Section Text", part_id=part.part_id)
    db_session.add(section)
    db_session.flush()

    question = Question(question_number=1, text="Test Q?", section_id=section.section_id)
    db_session.add(question)
    db_session.flush()

    option1 = Option(text="Opt 1", is_correct=True, question_id=question.question_id)
    option2 = Option(text="Opt 2", is_correct=False, question_id=question.question_id)
    db_session.add_all([option1, option2])
    db_session.commit()

    # Test get_parts
    parts = quiz_service.get_parts(db_session)
    assert len(parts) >= 1
    
    # Test get_part_by_id
    fetched_part = quiz_service.get_part_by_id(db_session, part.part_id)
    assert fetched_part is not None
    assert fetched_part.part_id == part.part_id

    # Test get_sections_by_part
    sections = quiz_service.get_sections_by_part(db_session, part.part_id)
    assert len(sections) == 1
    assert sections[0].section_id == section.section_id

    # Test get_section_by_id
    fetched_section = quiz_service.get_section_by_id(db_session, section.section_id)
    assert fetched_section is not None
    assert fetched_section.section_id == section.section_id

    # Test get_question_by_id
    fetched_q = quiz_service.get_question_by_id(db_session, question.question_id)
    assert fetched_q is not None
    assert fetched_q.question_id == question.question_id

    # Test get_options_by_question
    options = quiz_service.get_options_by_question(db_session, question.question_id)
    assert len(options) == 2
