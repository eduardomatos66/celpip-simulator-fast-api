"""
Answer domain models.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy import Integer, String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AnswerSheet(Base):
    __tablename__ = "answer_sheet"

    answer_sheet_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    test_id: Mapped[str] = mapped_column(String(255))
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User")
    
    date: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    option_answers: Mapped[List["OptionAnswer"]] = relationship(
        "OptionAnswer", back_populates="answer_sheet", cascade="all, delete-orphan"
    )


class OptionAnswer(Base):
    __tablename__ = "option_answer"

    option_answer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    answer_sheet_id: Mapped[Optional[int]] = mapped_column(ForeignKey("answer_sheet.answer_sheet_id"))
    
    question_id: Mapped[str] = mapped_column(String(255))
    user_answer: Mapped[Optional[str]] = mapped_column(Text)      # length=5000 in Java
    correct_answer: Mapped[Optional[str]] = mapped_column(Text)   # length=8000 in Java
    duration: Mapped[Optional[float]] = mapped_column(Float)

    answer_sheet: Mapped[Optional["AnswerSheet"]] = relationship("AnswerSheet", back_populates="option_answers")


class TestResult(Base):
    __tablename__ = "test_result"

    test_result_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    listening_corrects: Mapped[Optional[int]] = mapped_column(Integer)
    listening_max: Mapped[Optional[float]] = mapped_column(Float)
    
    reading_corrects: Mapped[Optional[int]] = mapped_column(Integer)
    reading_max: Mapped[Optional[float]] = mapped_column(Float)
    
    writing_min: Mapped[Optional[float]] = mapped_column(Float)
    writing_max: Mapped[Optional[float]] = mapped_column(Float)
    
    speaking_min: Mapped[Optional[float]] = mapped_column(Float)
    speaking_max: Mapped[Optional[float]] = mapped_column(Float)
    
    clb_min: Mapped[Optional[float]] = mapped_column(Float)
    clb_max: Mapped[Optional[float]] = mapped_column(Float)
    clb_average: Mapped[Optional[float]] = mapped_column(Float)
    
    result_date: Mapped[Optional[datetime]] = mapped_column("result_date", DateTime)

    available_test_id: Mapped[Optional[int]] = mapped_column(ForeignKey("test_available.available_test_id"))
    test_available: Mapped[Optional["TestAvailable"]] = relationship("TestAvailable")

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    user: Mapped[Optional["User"]] = relationship("User")
    
    answer_sheet_id: Mapped[Optional[int]] = mapped_column(ForeignKey("answer_sheet.answer_sheet_id"))
    
    # We explicitly import string references for models to avoid circular imports below
    # Note: "User" and "TestAvailable" need to be mapped appropriately by SQLAlchemy
