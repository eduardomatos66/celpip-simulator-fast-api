from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.quiz import TestAvailableRead
from app.schemas.user import UserRead

# --- Option Answer ---
class OptionAnswerBase(BaseModel):
    question_id: str = Field(..., description="The ID of the question being answered", examples=["1"])
    user_answer: Optional[str] = Field(None, description="The option selected by the user", examples=["Option A"])
    duration: Optional[float] = Field(None, description="Time spent on this question in seconds", examples=[45.5])

class OptionAnswerCreate(OptionAnswerBase):
    pass

class OptionAnswerRead(OptionAnswerBase):
    option_answer_id: int = Field(..., description="Unique ID for the stored answer")
    answer_sheet_id: Optional[int] = Field(None, description="The parent answer sheet ID")
    correct_answer: Optional[str] = Field(None, description="The actual correct answer (returned for review)")
    model_config = ConfigDict(from_attributes=True)

# --- Answer Sheet ---
class AnswerSheetBase(BaseModel):
    test_id: str = Field(..., description="The ID of the test being submitted", examples=["1"])

class AnswerSheetCreate(AnswerSheetBase):
    option_answers: List[OptionAnswerCreate] = Field([], description="List of individual question answers")

class AnswerSheetRead(AnswerSheetBase):
    answer_sheet_id: int = Field(..., description="Unique identifier for the answer sheet")
    user_id: int = Field(..., description="Owner's user ID")
    date: datetime = Field(..., description="Submission timestamp")
    option_answers: List[OptionAnswerRead] = Field([], description="Detailed record of question-by-question answers")
    model_config = ConfigDict(from_attributes=True)

# --- Test Result ---
class TestResultBase(BaseModel):
    listening_corrects: Optional[int] = Field(None, description="Number of correct answers in Listening")
    listening_max: Optional[float] = Field(None, description="Maximum possible score in Listening")
    reading_corrects: Optional[int] = Field(None, description="Number of correct answers in Reading")
    reading_max: Optional[float] = Field(None, description="Maximum possible score in Reading")
    writing_min: Optional[float] = Field(None, description="Minimum estimated score in Writing")
    writing_max: Optional[float] = Field(None, description="Maximum estimated score in Writing")
    speaking_min: Optional[float] = Field(None, description="Minimum estimated score in Speaking")
    speaking_max: Optional[float] = Field(None, description="Maximum estimated score in Speaking")
    clb_min: Optional[float] = Field(None, description="Minimum estimated CLB level")
    clb_max: Optional[float] = Field(None, description="Maximum estimated CLB level")
    clb_average: Optional[float] = Field(None, description="Overall average CLB level calculated")
    result_date: Optional[datetime] = Field(None, description="Timestamp when the result was generated")

class TestResultCreate(TestResultBase):
    available_test_id: Optional[int] = Field(None, description="The test ID this result belongs to")
    answer_sheet_id: Optional[int] = Field(None, description="The answer sheet ID this result belongs to")

class TestResultRead(TestResultBase):
    test_result_id: int = Field(..., description="Unique identifier for the test result")
    user_id: Optional[int] = Field(None, description="The user's ID")
    answer_sheet_id: Optional[int] = Field(None, description="The linked answer sheet ID")
    available_test_id: Optional[int] = Field(None, description="The linked test ID")
    test_name: Optional[str] = Field(None, description="The name of the test")
    model_config = ConfigDict(from_attributes=True)

class TestResultDetail(TestResultRead):
    option_answers: List[OptionAnswerRead] = Field([], description="Detailed record of question-by-question answers")

class TestResultRequest(BaseModel):
    test_id: int = Field(..., description="The ID of the test to analyze", examples=[1])
    name: str = Field(..., description="The name of the test for identification", examples=["CELPIP Test 1"])
