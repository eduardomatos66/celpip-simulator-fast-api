from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.quiz import AreaTest

# --- Options ---
class OptionBase(BaseModel):
    text: Optional[str] = None
    is_correct: Optional[bool] = False

class OptionCreate(OptionBase):
    pass

class OptionUpdate(OptionBase):
    pass

class OptionRead(OptionBase):
    option_id: int
    question_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

# --- Questions ---
class QuestionBase(BaseModel):
    question_number: Optional[int] = None
    time: Optional[int] = None
    audio_link: Optional[str] = None
    text: Optional[str] = None

class QuestionCreate(QuestionBase):
    options: List[OptionCreate] = []

class QuestionUpdate(QuestionBase):
    pass

class QuestionRead(QuestionBase):
    question_id: int
    section_id: Optional[int] = None
    options: List[OptionRead] = []
    model_config = ConfigDict(from_attributes=True)

# --- Sections ---
class SectionBase(BaseModel):
    section_number: Optional[int] = None
    text: Optional[str] = None
    time: Optional[int] = None
    section_audio_link: Optional[str] = None
    section_image_link: Optional[str] = None
    section_video_link: Optional[str] = None
    text_question_content: Optional[str] = None

class SectionCreate(SectionBase):
    questions: List[QuestionCreate] = []

class SectionUpdate(SectionBase):
    pass

class SectionRead(SectionBase):
    section_id: int
    part_id: Optional[int] = None
    questions: List[QuestionRead] = []
    model_config = ConfigDict(from_attributes=True)

# --- Part Introduction ---
class PartIntroductionBase(BaseModel):
    text: Optional[str] = None
    auxiliary_texts: Optional[str] = None

class PartIntroductionCreate(PartIntroductionBase):
    pass

class PartIntroductionUpdate(PartIntroductionBase):
    pass

class PartIntroductionRead(PartIntroductionBase):
    part_introduction_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Parts ---
class PartBase(BaseModel):
    part_number: Optional[int] = None
    part_name: Optional[str] = None
    text_question_content: Optional[str] = None
    time: Optional[int] = None
    questions_type: Optional[str] = None

class PartCreate(PartBase):
    introduction: Optional[PartIntroductionCreate] = None
    sections: List[SectionCreate] = []

class PartUpdate(PartBase):
    pass

class PartRead(PartBase):
    part_id: int
    introduction: Optional[PartIntroductionRead] = None
    sections: List[SectionRead] = []
    model_config = ConfigDict(from_attributes=True)

# --- Test Areas ---
class TestAreaBase(BaseModel):
    area: AreaTest
    part_id: Optional[int] = None

class TestAreaCreate(TestAreaBase):
    __test__ = False

class TestAreaUpdate(TestAreaBase):
    __test__ = False

class TestAreaRead(TestAreaBase):
    test_area_id: int
    available_test_id: Optional[int] = None
    part: Optional[PartRead] = None
    model_config = ConfigDict(from_attributes=True)

# --- Test Available ---
class TestAvailableBase(BaseModel):
    test_name: str

class TestAvailableCreate(TestAvailableBase):
    test_areas: List[TestAreaCreate] = []

class TestAvailableUpdate(TestAvailableBase):
    pass

class TestAvailableRead(TestAvailableBase):
    test_id: int
    test_areas: List[TestAreaRead] = []
    model_config = ConfigDict(from_attributes=True)
