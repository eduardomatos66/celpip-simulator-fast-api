"""
SQLAlchemy models package.
"""

from app.core.database import Base

from app.models.user import User
from app.models.quiz import (
    TestAvailable,
    TestArea,
    PartIntroduction,
    Part,
    Section,
    Question,
    Option,
    AreaTest,
)
from app.models.answer import (
    AnswerSheet,
    OptionAnswer,
    TestResult,
)

# Export everything needed to initialize the DB and migrations
__all__ = [
    "Base",
    "User",
    "TestAvailable",
    "TestArea",
    "PartIntroduction",
    "Part",
    "Section",
    "Question",
    "Option",
    "AreaTest",
    "AnswerSheet",
    "OptionAnswer",
    "TestResult",
]
