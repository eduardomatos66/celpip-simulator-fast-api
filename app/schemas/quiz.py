from typing import List, Optional, Any, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, AliasChoices
from app.models.quiz import AreaTest

# --- Options ---
class OptionBase(BaseModel):
    text: Optional[str] = Field(None, description="The display text for this option", examples=["Option A"])
    is_correct: Optional[bool] = Field(False, description="Whether this is the correct answer to the question")

class OptionCreate(OptionBase):
    pass

class OptionUpdate(OptionBase):
    pass

class OptionRead(BaseModel):
    option_id: str = Field(..., description="Unique identifier for the option")
    text: str = Field(..., description="The display text for this option", examples=["Option A"])
    model_config = ConfigDict(from_attributes=True)

    @field_validator("option_id", mode="before")
    @classmethod
    def transform_id_to_str(cls, v: Any) -> str:
        return str(v)

# --- Questions ---
class QuestionBase(BaseModel):
    question_number: Optional[int] = Field(None, description="Ordered number of the question in its section", examples=[1])
    time: Optional[int] = Field(None, description="Time limit for this specific question in seconds", examples=[60])
    audio_link: Optional[str] = Field(None, description="URL to an audio file associated with the question", examples=["https://example.com/audio/q1.mp3"])
    text: Optional[str] = Field(None, description="The question text or prompt", examples=["What was the main topic of the conversation?"])

class QuestionCreate(QuestionBase):
    options: List[OptionCreate] = Field([], description="List of possible options for this question")

class QuestionUpdate(QuestionBase):
    pass

class QuestionRead(QuestionBase):
    question_id: Union[int, str] = Field(..., description="Unique identifier for the question")
    question_number: int = Field(..., description="Ordered number of the question in its section", examples=[1])
    options: Optional[List[OptionRead]] = Field(default_factory=list, description="List of options for this question")
    model_config = ConfigDict(from_attributes=True)

    @field_validator("question_id", mode="before")
    @classmethod
    def transform_id_to_str(cls, v: Any) -> str:
         return str(v)

# --- Sections ---
class SectionBase(BaseModel):
    section_number: Optional[int] = Field(None, description="Ordered number of the section in its part", examples=[1])
    text: Optional[str] = Field(None, description="Descriptive text or instructions for the section")
    time: Optional[int] = Field(None, description="Time limit for this section in seconds", examples=[300])
    section_audio_link: Optional[str] = Field(None, description="URL to the main audio for this section")
    section_image_link: Optional[str] = Field(None, description="URL to an image for this section")
    section_video_link: Optional[str] = Field(None, description="URL to a video for this section")
    text_question_content: Optional[str] = Field(None, description="Main text content for reading or writing sections")

class SectionCreate(SectionBase):
    questions: List[QuestionCreate] = Field([], description="List of questions within this section")

class SectionUpdate(SectionBase):
    pass

class SectionRead(SectionBase):
    section_id: str = Field(..., description="Unique identifier for the section")
    section_number: int = Field(..., description="Ordered number of the section in its part", examples=[1])
    introductions: Optional[List[str]] = Field(None, description="Optional list of introductions for the section")
    questions: List[QuestionRead] = Field([], description="List of questions in this section")
    model_config = ConfigDict(from_attributes=True)

    @field_validator("section_id", mode="before")
    @classmethod
    def transform_id_to_str(cls, v: Any) -> str:
        return str(v)

# --- Part Introduction ---
class PartIntroductionBase(BaseModel):
    text: Optional[str] = Field(None, description="Introduction text for the part")
    auxiliary_texts: Optional[str] = Field(None, description="Additional context or shared information for the part")

class PartIntroductionCreate(PartIntroductionBase):
    pass

class PartIntroductionUpdate(PartIntroductionBase):
    pass

class PartIntroductionRead(BaseModel):
    text: str = Field(..., description="Introduction text for the part")
    auxiliary_texts: str = Field(..., description="Additional context or shared information for the part")
    model_config = ConfigDict(from_attributes=True)

# --- Parts ---
class PartBase(BaseModel):
    part_number: Optional[int] = Field(None, description="Ordered number of the part", examples=[1])
    part_name: Optional[str] = Field(None, description="Name of the part (e.g., 'Listening Part 1')", examples=["Part 1"])
    text_question_content: Optional[str] = Field(None, description="Global text content for this part if applicable")
    time: Optional[int] = Field(None, description="Total time allocated for this part", examples=[600])
    questions_type: Optional[str] = Field(None, description="Type of questions in this part (e.g., 'MCQ')", examples=["MCQ"])

class PartCreate(PartBase):
    introduction: Optional[PartIntroductionCreate] = None
    sections: List[SectionCreate] = Field([], description="List of sections in this part")

class PartUpdate(PartBase):
    pass

class PartRead(PartBase):
    part_id: int = Field(..., description="Unique identifier for the part")
    part_number: int = Field(..., description="Ordered number of the part", examples=[1])
    part_name: str = Field(..., description="Name of the part (e.g., 'Listening Part 1')", examples=["Part 1"])
    questions_type: str = Field(..., description="Type of questions in this part (e.g., 'MCQ')", examples=["MCQ"])
    introduction: Optional[PartIntroductionRead] = None
    sections: List[SectionRead] = Field([], description="List of sections in this part")
    model_config = ConfigDict(from_attributes=True)

# --- Test Areas ---
class TestAreaBase(BaseModel):
    area: AreaTest = Field(..., description="The area of the test (LISTENING, READING, WRITING, SPEAKING)")

class TestAreaCreate(TestAreaBase):
    __test__ = False

class TestAreaUpdate(TestAreaBase):
    __test__ = False

class TestAreaRead(BaseModel):
    area_id: str = Field(
        ...,
        description="Unique identifier for the test area record",
        validation_alias=AliasChoices("area_id", "test_area_id")
    )
    area_name: AreaTest = Field(..., description="The area of the test (LISTENING, READING, WRITING, SPEAKING)")
    time: Optional[int] = Field(None, description="Optional time for the test area")
    parts: List[PartRead] = Field([], description="The list of parts in this area")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_validator("area_id", mode="before")
    @classmethod
    def transform_id_to_str(cls, v: Any) -> str:
        return str(v)

    @field_validator("area_name", mode="before")
    @classmethod
    def normalize_area_name(cls, v: Any) -> str:
        if isinstance(v, str):
            return v.lower()
        return v


# --- Test Available ---
class TestAvailableBase(BaseModel):
    test_name: str = Field(..., description="The name of the test", examples=["CELPIP Sample Test 1"])

class TestAvailableCreate(TestAvailableBase):
    test_areas: List[TestAreaCreate] = Field([], description="List of test areas (Listening, Reading, etc.) to include in this test")

class TestAvailableUpdate(TestAvailableBase):
    pass

class TestAvailableRead(TestAvailableBase):
    test_id: str = Field(..., description="Unique identifier for the test")
    user_name: Optional[str] = Field(None, description="The name of the user taking the test")
    date: Optional[str] = Field(None, description="The date the test was taken or requested")
    test_areas: List[TestAreaRead] = Field([], description="Hierarchical data for all areas of this test")
    model_config = ConfigDict(from_attributes=True)

    @field_validator("test_id", mode="before")
    @classmethod
    def transform_id_to_str(cls, v: Any) -> str:
        return str(v)


class TestAvailableMinimalRead(BaseModel):
    test_id: str = Field(..., description="Unique identifier for the test")
    test_name: str = Field(..., description="The name of the test", examples=["CELPIP Sample Test 1"])
    model_config = ConfigDict(from_attributes=True)

    @field_validator("test_id", mode="before")
    @classmethod
    def transform_id_to_str(cls, v: Any) -> str:
        return str(v)
