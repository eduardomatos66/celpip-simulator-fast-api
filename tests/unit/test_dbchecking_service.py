import pytest
from unittest.mock import patch
from app.services import dbchecking_service
from app.models.quiz import Option, Question, Section, Part, TestArea

@pytest.mark.asyncio
async def test_check_url_validity():
    with patch("httpx.AsyncClient.head") as mock_head:
        # Mock successful HEAD
        mock_head.return_value.status_code = 200
        assert await dbchecking_service.check_url_validity("http://valid.com") is True

        # Mock 404
        mock_head.return_value.status_code = 404
        assert await dbchecking_service.check_url_validity("http://invalid.com") is False

        # Mock Exception
        mock_head.side_effect = Exception("Timeout")
        assert await dbchecking_service.check_url_validity("http://timeout.com") is False

        # Mock Invalid URLs
        assert await dbchecking_service.check_url_validity(None) is False
        assert await dbchecking_service.check_url_validity("") is False
        assert await dbchecking_service.check_url_validity("ftp://wrong.com") is False

@pytest.mark.asyncio
async def test_check_links(db_session):
    # Setup dummy entities with missing external URLs
    q = Question(question_id=987, audio_link="http://bad-audio.com")
    db_session.add(q)
    db_session.commit()

    with patch("app.services.dbchecking_service.check_url_validity", return_value=False):
        result = await dbchecking_service.check_links(db_session)
        assert result["issues_found"] >= 1
        assert any("bad-audio.com" in d for d in result["details"])

def test_check_non_valid_questions(db_session):
    # Create a question with NO correct answers
    q = Question(question_id=999, text="No correct options")
    db_session.add(q)
    db_session.flush()
    o = Option(option_id=9991, text="A", is_correct=False, questions=[q])
    db_session.add(o)
    db_session.commit()

    result = dbchecking_service.check_non_valid_questions(db_session)
    assert result["invalid_questions_count"] >= 1
    assert q.question_id in result["question_ids"]

def test_check_orphan_entities(db_session):
    # Add an orphaned option
    orphaned_option = Option(option_id=8888, text="Orphan")
    db_session.add(orphaned_option)
    db_session.commit()

    result = dbchecking_service.check_orphan_entities(db_session)
    # The count should reflect options deleted
    assert result["deleted"]["options"] >= 1

    # Confirm it was deleted
    assert db_session.query(Option).filter_by(option_id=8888).first() is None

@pytest.mark.asyncio
async def test_check_links_full(db_session):
    # Create section with all link types
    sec = Section(
        section_id=123,
        section_image_link="http://test.com/img.png",
        section_audio_link="http://test.com/aud.mp3",
        section_video_link="http://test.com/vid.mp4"
    )
    db_session.add(sec)
    db_session.commit()

    with patch("app.services.dbchecking_service.check_url_validity", return_value=False):
        result = await dbchecking_service.check_links(db_session)
        assert result["issues_found"] >= 3
        assert any("Section ID 123 invalid image" in d for d in result["details"])
        assert any("Section ID 123 invalid audio" in d for d in result["details"])
        assert any("Section ID 123 invalid video" in d for d in result["details"])
