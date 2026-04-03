from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.quiz import AreaTest

# --- Options ---
class OptionBase(BaseModel):
    text: Optional[str] = Field(None, description="The display text for this option", examples=["Option A"])
    is_correct: Optional[bool] = Field(False, description="Whether this is the correct answer to the question")

class OptionCreate(OptionBase):
    pass

class OptionUpdate(OptionBase):
    pass

class OptionRead(OptionBase):
    option_id: int = Field(..., description="Unique identifier for the option")
    question_id: Optional[int] = Field(None, description="The ID of the question this option belongs to")
    model_config = ConfigDict(from_attributes=True)

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
    question_id: int = Field(..., description="Unique identifier for the question")
    section_id: Optional[int] = Field(None, description="The ID of the section this question belongs to")
    options: List[OptionRead] = Field([], description="List of options for this question")
    model_config = ConfigDict(from_attributes=True)

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
    section_id: int = Field(..., description="Unique identifier for the section")
    part_id: Optional[int] = Field(None, description="The ID of the part this section belongs to")
    questions: List[QuestionRead] = Field([], description="List of questions in this section")
    model_config = ConfigDict(from_attributes=True)

# --- Part Introduction ---
class PartIntroductionBase(BaseModel):
    text: Optional[str] = Field(None, description="Introduction text for the part")
    auxiliary_texts: Optional[str] = Field(None, description="Additional context or shared information for the part")

class PartIntroductionCreate(PartIntroductionBase):
    pass

class PartIntroductionUpdate(PartIntroductionBase):
    pass

class PartIntroductionRead(PartIntroductionBase):
    part_introduction_id: int = Field(..., description="Unique identifier for the part introduction")
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
    introduction: Optional[PartIntroductionRead] = None
    sections: List[SectionRead] = Field([], description="List of sections in this part")
    model_config = ConfigDict(from_attributes=True)

# --- Test Areas ---
class TestAreaBase(BaseModel):
    area: AreaTest = Field(..., description="The area of the test (LISTENING, READING, WRITING, SPEAKING)")
    part_id: Optional[int] = Field(None, description="The ID of the first part in this area")

class TestAreaCreate(TestAreaBase):
    __test__ = False

class TestAreaUpdate(TestAreaBase):
    __test__ = False

class TestAreaRead(TestAreaBase):
    test_area_id: int = Field(..., description="Unique identifier for the test area record")
    available_test_id: Optional[int] = Field(None, description="The ID of the parent test")
    part: Optional[PartRead] = Field(None, description="The full hierarchy of parts, sections, and questions")
    model_config = ConfigDict(from_attributes=True)

# --- Test Available ---
class TestAvailableBase(BaseModel):
    test_name: str = Field(..., description="The name of the test", examples=["CELPIP Sample Test 1"])

class TestAvailableCreate(TestAvailableBase):
    test_areas: List[TestAreaCreate] = Field([], description="List of test areas (Listening, Reading, etc.) to include in this test")

class TestAvailableUpdate(TestAvailableBase):
    pass

class TestAvailableRead(TestAvailableBase):
    test_id: int = Field(..., description="Unique identifier for the test")
    test_areas: List[TestAreaRead] = Field([], description="Hierarchical data for all areas of this test")
    model_config = ConfigDict(from_attributes=True)

class TestAvailableMinimalRead(BaseModel):
    test_id: int = Field(..., description="Unique identifier for the test")
    test_name: str = Field(..., description="The name of the test", examples=["CELPIP Sample Test 1"])
    model_config = ConfigDict(from_attributes=True)
