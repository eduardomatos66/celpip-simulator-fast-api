import asyncio
import logging
import httpx
from typing import List
from sqlalchemy.orm import Session
from app.models.quiz import Option, Question, Section, Part, TestArea, TestAvailable
from app.core.decorators import log_execution_time

logger = logging.getLogger(__name__)

@log_execution_time
async def check_url_validity(url: str) -> bool:
    """Async check if a URL is valid/available."""
    if not url or not url.startswith("http"):
        return False
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.head(url, follow_redirects=True)
            return resp.status_code < 400
    except Exception:
        return False

@log_execution_time
async def check_links(db: Session) -> dict:
    """Finds dead links in options, questions, and sections."""
    issues = []

    # Options
    for option in db.query(Option).all():
        if option.text and option.text.startswith("http"):
            if not await check_url_validity(option.text):
                issues.append(f"Option ID {option.option_id} invalid link: {option.text}")

    # Questions
    for question in db.query(Question).all():
        if question.audio_link and question.audio_link.startswith("http"):
            if not await check_url_validity(question.audio_link):
                issues.append(f"Question ID {question.question_id} invalid audio: {question.audio_link}")

    # Sections
    for section in db.query(Section).all():
        links = [
            ("image", section.section_image_link),
            ("audio", section.section_audio_link),
            ("video", section.section_video_link)
        ]
        for l_type, link in links:
            if link and link.startswith("http"):
                if not await check_url_validity(link):
                    issues.append(f"Section ID {section.section_id} invalid {l_type}: {link}")

    for issue in issues:
        logger.warning(issue)

    return {"issues_found": len(issues), "details": issues}


@log_execution_time
def check_non_valid_questions(db: Session) -> dict:
    """Finds questions that don't have any option marked as correct."""
    invalid_qs = []
    for question in db.query(Question).all():
        if question.options:
            has_correct = any(opt.is_correct for opt in question.options)
            if not has_correct:
                invalid_qs.append(question.question_id)
                logger.warning(f"Question {question.question_id} has no correct option.")

    return {"invalid_questions_count": len(invalid_qs), "question_ids": invalid_qs}


@log_execution_time
def check_orphan_entities(db: Session) -> dict:
    """Finds and deletes orphaned entities (no parents)."""
    deleted_counts = {}

    # Options (orphan if not linked to any existing question in question_options table)
    from app.models.quiz import question_options, section_questions, part_sections, test_area_parts, test_available_test_areas

    # Options
    linked_option_ids = {row.options_option_id for row in db.query(question_options).all()}
    orphaned_opts = [o for o in db.query(Option).all() if o.option_id not in linked_option_ids]
    if orphaned_opts:
        for o in orphaned_opts: db.delete(o)
        deleted_counts["options"] = len(orphaned_opts)

    # Questions
    linked_question_ids = {row.questions_question_id for row in db.query(section_questions).all()}
    orphaned_qs = [q for q in db.query(Question).all() if q.question_id not in linked_question_ids]
    if orphaned_qs:
        for q in orphaned_qs: db.delete(q)
        deleted_counts["questions"] = len(orphaned_qs)

    # Sections
    linked_section_ids = {row.sections_section_id for row in db.query(part_sections).all()}
    orphaned_secs = [s for s in db.query(Section).all() if s.section_id not in linked_section_ids]
    if orphaned_secs:
        for s in orphaned_secs: db.delete(s)
        deleted_counts["sections"] = len(orphaned_secs)

    # Parts
    linked_part_ids = {row.parts_part_id for row in db.query(test_area_parts).all()}
    orphaned_parts = [p for p in db.query(Part).all() if p.part_id not in linked_part_ids]
    if orphaned_parts:
        for p in orphaned_parts: db.delete(p)
        deleted_counts["parts"] = len(orphaned_parts)

    # TestAreas
    linked_area_ids = {row.test_areas_area_id for row in db.query(test_available_test_areas).all()}
    orphaned_tas = [ta for ta in db.query(TestArea).all() if ta.test_area_id not in linked_area_ids]
    if orphaned_tas:
        for ta in orphaned_tas: db.delete(ta)
        deleted_counts["test_areas"] = len(orphaned_tas)

    db.commit()
    return {"deleted": deleted_counts}
