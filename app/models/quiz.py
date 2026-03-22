"""
Quiz domain models mapping to the Java entities.
"""

import enum
from typing import Optional, List

from sqlalchemy import Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AreaTest(str, enum.Enum):
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"


class TestAvailable(Base):
    __tablename__ = "test_available"

    test_id: Mapped[int] = mapped_column("available_test_id", primary_key=True, autoincrement=True)
    test_name: Mapped[str] = mapped_column(String(255))
    
    test_areas: Mapped[List["TestArea"]] = relationship(
        "TestArea", back_populates="test_available", cascade="all, delete-orphan"
    )


class TestArea(Base):
    __tablename__ = "test_area"

    test_area_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    available_test_id: Mapped[Optional[int]] = mapped_column(ForeignKey("test_available.available_test_id"))
    
    area: Mapped[AreaTest] = mapped_column(Enum(AreaTest))
    
    # A single part representing this specific test area
    part_id: Mapped[Optional[int]] = mapped_column(ForeignKey("part.part_id"))
    part: Mapped[Optional["Part"]] = relationship("Part")
    
    test_available: Mapped[Optional["TestAvailable"]] = relationship(
        "TestAvailable", back_populates="test_areas"
    )


class PartIntroduction(Base):
    __tablename__ = "part_introduction"

    part_introduction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[Optional[str]] = mapped_column(Text)
    auxiliary_texts: Mapped[Optional[str]] = mapped_column(Text)  # length=5000 in Java


class Part(Base):
    __tablename__ = "part"

    part_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    part_number: Mapped[Optional[int]] = mapped_column(Integer)
    part_name: Mapped[Optional[str]] = mapped_column(String(255))
    text_question_content: Mapped[Optional[str]] = mapped_column(Text)  # length=5000 in Java
    time: Mapped[Optional[int]] = mapped_column(Integer)
    questions_type: Mapped[Optional[str]] = mapped_column(String(255))

    introduction_id: Mapped[Optional[int]] = mapped_column(ForeignKey("part_introduction.part_introduction_id"))
    introduction: Mapped[Optional["PartIntroduction"]] = relationship("PartIntroduction")

    sections: Mapped[List["Section"]] = relationship(
        "Section", back_populates="part", cascade="all, delete-orphan"
    )


class Section(Base):
    __tablename__ = "section"

    section_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    part_id: Mapped[Optional[int]] = mapped_column(ForeignKey("part.part_id"))
    
    section_number: Mapped[Optional[int]] = mapped_column(Integer)
    text: Mapped[Optional[str]] = mapped_column(Text)  # length=5000 in Java
    time: Mapped[Optional[int]] = mapped_column(Integer)
    section_audio_link: Mapped[Optional[str]] = mapped_column(String(2000))
    section_image_link: Mapped[Optional[str]] = mapped_column(String(2000))
    section_video_link: Mapped[Optional[str]] = mapped_column(String(2000))
    text_question_content: Mapped[Optional[str]] = mapped_column(Text)  # length=5000 in Java

    part: Mapped[Optional["Part"]] = relationship("Part", back_populates="sections")
    
    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="section", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "question"

    question_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    section_id: Mapped[Optional[int]] = mapped_column(ForeignKey("section.section_id"))
    
    question_number: Mapped[Optional[int]] = mapped_column(Integer)
    time: Mapped[Optional[int]] = mapped_column(Integer)
    audio_link: Mapped[Optional[str]] = mapped_column(String(2000))
    text: Mapped[Optional[str]] = mapped_column(Text)

    section: Mapped[Optional["Section"]] = relationship("Section", back_populates="questions")

    options: Mapped[List["Option"]] = relationship(
        "Option", back_populates="question", cascade="all, delete-orphan"
    )


class Option(Base):
    __tablename__ = "question_option"

    option_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[Optional[int]] = mapped_column(ForeignKey("question.question_id"))
    
    text: Mapped[Optional[str]] = mapped_column(Text)
    is_correct: Mapped[Optional[bool]] = mapped_column("is_correct", default=False)
    
    question: Mapped[Optional["Question"]] = relationship("Question", back_populates="options")
