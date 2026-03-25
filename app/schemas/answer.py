from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.quiz import TestAvailableRead
from app.schemas.user import UserRead

# --- Option Answer ---
class OptionAnswerBase(BaseModel):
    question_id: str
    user_answer: Optional[str] = None
    duration: Optional[float] = None

class OptionAnswerCreate(OptionAnswerBase):
    # correct_answer is not provided by the user, the server calculates it!
    pass

class OptionAnswerRead(OptionAnswerBase):
    option_answer_id: int
    answer_sheet_id: Optional[int] = None
    correct_answer: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# --- Answer Sheet ---
class AnswerSheetBase(BaseModel):
    test_id: str

class AnswerSheetCreate(AnswerSheetBase):
    option_answers: List[OptionAnswerCreate] = []

class AnswerSheetRead(AnswerSheetBase):
    answer_sheet_id: int
    user_id: int
    date: datetime
    option_answers: List[OptionAnswerRead] = []
    model_config = ConfigDict(from_attributes=True)

# --- Test Result ---
class TestResultBase(BaseModel):
    listening_corrects: Optional[int] = None
    listening_max: Optional[float] = None
    reading_corrects: Optional[int] = None
    reading_max: Optional[float] = None
    writing_min: Optional[float] = None
    writing_max: Optional[float] = None
    speaking_min: Optional[float] = None
    speaking_max: Optional[float] = None
    clb_min: Optional[float] = None
    clb_max: Optional[float] = None
    clb_average: Optional[float] = None
    result_date: Optional[datetime] = None

class TestResultCreate(TestResultBase):
    available_test_id: Optional[int] = None
    answer_sheet_id: Optional[int] = None

class TestResultRead(TestResultBase):
    test_result_id: int
    user_id: Optional[int] = None
    answer_sheet_id: Optional[int] = None
    available_test_id: Optional[int] = None
    # We might nest the user or test data depending on the exact API response required
    model_config = ConfigDict(from_attributes=True)

class TestResultRequest(BaseModel):
    test_id: int
    name: str
