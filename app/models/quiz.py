from typing import Optional, List
import enum

from sqlalchemy import Integer, String, Text, ForeignKey, Enum, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AreaTest(str, enum.Enum):
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"


# --- Association Tables (Matching Legacy SQL Schema Exactly) ---

test_available_test_areas = Table(
    "test_available_test_areas",
    Base.metadata,
    Column("test_available_available_test_id", Integer, ForeignKey("test_available.available_test_id"), primary_key=True),
    Column("test_areas_area_id", Integer, ForeignKey("test_area.area_id"), primary_key=True),
)

test_area_parts = Table(
    "test_area_parts",
    Base.metadata,
    Column("test_area_area_id", Integer, ForeignKey("test_area.area_id"), primary_key=True),
    Column("parts_part_id", Integer, ForeignKey("part.part_id"), primary_key=True),
)

part_sections = Table(
    "part_sections",
    Base.metadata,
    Column("part_part_id", Integer, ForeignKey("part.part_id"), primary_key=True),
    Column("sections_section_id", Integer, ForeignKey("section.section_id"), primary_key=True),
)

section_questions = Table(
    "section_questions",
    Base.metadata,
    Column("section_section_id", Integer, ForeignKey("section.section_id"), primary_key=True),
    Column("questions_question_id", Integer, ForeignKey("question.question_id"), primary_key=True),
)

question_options = Table(
    "question_options",
    Base.metadata,
    Column("question_question_id", Integer, ForeignKey("question.question_id"), primary_key=True),
    Column("options_option_id", Integer, ForeignKey("question_option.option_id"), primary_key=True),
)


# --- Models ---

class TestAvailable(Base):
    __tablename__ = "test_available"
    __test__ = False

    test_id: Mapped[int] = mapped_column("available_test_id", primary_key=True, autoincrement=True)
    test_name: Mapped[str] = mapped_column(String(255))

    test_areas: Mapped[List["TestArea"]] = relationship(
        "TestArea",
        secondary=test_available_test_areas,
        back_populates="test_available"
    )


class TestArea(Base):
    __tablename__ = "test_area"
    __test__ = False

    test_area_id: Mapped[int] = mapped_column("area_id", primary_key=True, autoincrement=True)
    area_name: Mapped[str] = mapped_column("area_name", String(255))

    @property
    def area(self) -> AreaTest:
        """Helper to map area_name string to AreaTest enum."""
        try:
            return AreaTest(self.area_name.lower())
        except (ValueError, AttributeError):
            return AreaTest.LISTENING # Default placeholder

    test_available: Mapped[List["TestAvailable"]] = relationship(
        "TestAvailable",
        secondary=test_available_test_areas,
        back_populates="test_areas"
    )

    parts: Mapped[List["Part"]] = relationship(
        "Part",
        secondary=test_area_parts,
        back_populates="test_areas"
    )


class PartIntroduction(Base):
    __tablename__ = "part_introduction"

    part_introduction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[Optional[str]] = mapped_column(Text)
    auxiliary_texts: Mapped[Optional[str]] = mapped_column(Text)


class Part(Base):
    __tablename__ = "part"

    part_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    part_number: Mapped[Optional[int]] = mapped_column(Integer)
    part_name: Mapped[Optional[str]] = mapped_column(String(255))
    text_question_content: Mapped[Optional[str]] = mapped_column(Text)
    time: Mapped[Optional[int]] = mapped_column(Integer)
    questions_type: Mapped[Optional[str]] = mapped_column(String(255))

    introduction_id: Mapped[Optional[int]] = mapped_column("introduction_part_introduction_id", ForeignKey("part_introduction.part_introduction_id"))
    introduction: Mapped[Optional["PartIntroduction"]] = relationship("PartIntroduction")

    test_areas: Mapped[List["TestArea"]] = relationship(
        "TestArea",
        secondary=test_area_parts,
        back_populates="parts"
    )

    sections: Mapped[List["Section"]] = relationship(
        "Section",
        secondary=part_sections,
        back_populates="parts"
    )


class Section(Base):
    __tablename__ = "section"

    section_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    section_number: Mapped[Optional[int]] = mapped_column(Integer)
    text: Mapped[Optional[str]] = mapped_column(Text)
    time: Mapped[Optional[int]] = mapped_column(Integer)
    section_audio_link: Mapped[Optional[str]] = mapped_column(String(2000))
    section_image_link: Mapped[Optional[str]] = mapped_column(String(2000))
    section_video_link: Mapped[Optional[str]] = mapped_column(String(2000))
    text_question_content: Mapped[Optional[str]] = mapped_column(Text)

    parts: Mapped[List["Part"]] = relationship(
        "Part",
        secondary=part_sections,
        back_populates="sections"
    )

    questions: Mapped[List["Question"]] = relationship(
        "Question",
        secondary=section_questions,
        back_populates="sections"
    )


class Question(Base):
    __tablename__ = "question"

    question_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_number: Mapped[Optional[int]] = mapped_column(Integer)
    time: Mapped[Optional[int]] = mapped_column(Integer)
    audio_link: Mapped[Optional[str]] = mapped_column(String(2000))
    text: Mapped[Optional[str]] = mapped_column(Text)

    sections: Mapped[List["Section"]] = relationship(
        "Section",
        secondary=section_questions,
        back_populates="questions"
    )

    options: Mapped[List["Option"]] = relationship(
        "Option",
        secondary=question_options,
        back_populates="questions"
    )


class Option(Base):
    __tablename__ = "question_option"

    option_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[Optional[str]] = mapped_column(Text)
    is_correct: Mapped[Optional[bool]] = mapped_column("is_correct", default=False)

    questions: Mapped[List["Question"]] = relationship(
        "Question",
        secondary=question_options,
        back_populates="options"
    )
