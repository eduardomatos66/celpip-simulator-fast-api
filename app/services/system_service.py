import shutil
import time
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.answer import AnswerSheet
from app.models.quiz import Question, TestArea, test_area_parts, part_sections, section_questions
from app.schemas.system_schemas import SystemHealth, SystemStats, DiskUsage

def get_uptime(start_time: datetime) -> Dict[str, Any]:
    uptime_seconds = (datetime.now() - start_time).total_seconds()

    # Human readable uptime
    days, rem = divmod(uptime_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    uptime_human = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
    return {
        "seconds": uptime_seconds,
        "human": uptime_human
    }

def get_disk_usage(path: str = "/") -> DiskUsage:
    total, used, free = shutil.disk_usage(path)
    # Convert to GB
    total_gb = total / (2**30)
    used_gb = used / (2**30)
    free_gb = free / (2**30)
    percent = (used / total) * 100

    return DiskUsage(
        total=round(total_gb, 2),
        used=round(used_gb, 2),
        free=round(free_gb, 2),
        percent=round(percent, 2)
    )

def check_db_health(db: Session) -> bool:
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def get_system_health(db: Session, start_time: datetime) -> SystemHealth:
    db_ok = check_db_health(db)
    uptime = get_uptime(start_time)
    disk = get_disk_usage()

    status = "ok" if db_ok and disk.percent < 95 else "warning"
    if disk.percent >= 99:
        status = "critical"

    return SystemHealth(
        status=status,
        database_connected=db_ok,
        disk_usage=disk,
        uptime_seconds=uptime["seconds"],
        uptime_human=uptime["human"]
    )

def get_system_stats(db: Session) -> SystemStats:
    # 1. Total answer sheets
    total_answers = db.query(func.count(AnswerSheet.answer_sheet_id)).scalar() or 0

    # 2. Total questions
    total_questions = db.query(func.count(Question.question_id)).scalar() or 0

    # 3. Questions per area
    # Join path: TestArea -> test_area_parts -> part_sections -> section_questions -> Question
    query = (
        db.query(TestArea.area_name, func.count(Question.question_id))
        .join(test_area_parts, TestArea.test_area_id == test_area_parts.c.test_area_area_id)
        .join(part_sections, test_area_parts.c.parts_part_id == part_sections.c.part_part_id)
        .join(section_questions, part_sections.c.sections_section_id == section_questions.c.section_section_id)
        .join(Question, section_questions.c.questions_question_id == Question.question_id)
        .group_by(TestArea.area_name)
    )

    results = query.all()
    questions_per_area = {name: count for name, count in results}

    # Add zeros for missing areas if needed (listening, reading, writing, speaking)
    for area in ["listening", "reading", "writing", "speaking"]:
        if area not in questions_per_area:
            # Check case sensitivity
            if area.capitalize() in questions_per_area:
                continue
            questions_per_area[area] = 0

    return SystemStats(
        total_answers_sheets=total_answers,
        total_questions=total_questions,
        questions_per_area=questions_per_area
    )
