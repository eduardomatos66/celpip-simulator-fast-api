from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
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
    start_time: Optional[str] = Field(None, description="Test start time ISO string", examples=["2024-03-20T10:00:00Z"])
    end_time: Optional[str] = Field(None, description="Test end time ISO string", examples=["2024-03-20T11:00:00Z"])

class AnswerSheetRead(AnswerSheetBase):
    answer_sheet_id: int = Field(..., description="Unique identifier for the answer sheet")
    user_id: int = Field(..., description="Owner's user ID")
    date: datetime = Field(..., description="Submission timestamp")
    option_answers: List[OptionAnswerRead] = Field([], description="Detailed record of question-by-question answers")
    start_time: Optional[str] = Field(None, description="Test start time ISO string")
    end_time: Optional[str] = Field(None, description="Test end time ISO string")
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

    # Frontend compatibility aliases
    test_available_name: Optional[str] = Field(None, description="Alias for test_name")
    date: Optional[datetime] = Field(None, description="Alias for result_date")
    listening: Optional[int] = Field(None, description="CLB level for Listening")
    reading: Optional[int] = Field(None, description="CLB level for Reading")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def populate_aliases(self) -> "TestResultRead":
        if self.test_name and not self.test_available_name:
            self.test_available_name = self.test_name
        if self.result_date and not self.date:
            self.date = self.result_date

        # Calculate CLB levels if missing (for frontend compatibility)
        if self.listening_corrects is not None and self.listening_max and self.listening_max > 0:
            percent = self.listening_corrects / self.listening_max
            if percent >= 0.92: self.listening = 10
            elif percent >= 0.86: self.listening = 9
            elif percent >= 0.78: self.listening = 8
            elif percent >= 0.71: self.listening = 7
            elif percent >= 0.58: self.listening = 6
            elif percent >= 0.44: self.listening = 5
            elif percent >= 0.29: self.listening = 4
            else: self.listening = 3 if self.listening_corrects > 0 else 0

        if self.reading_corrects is not None and self.reading_max and self.reading_max > 0:
            percent = self.reading_corrects / self.reading_max
            if percent >= 0.92: self.reading = 10
            elif percent >= 0.86: self.reading = 9
            elif percent >= 0.78: self.reading = 8
            elif percent >= 0.71: self.reading = 7
            elif percent >= 0.58: self.reading = 6
            elif percent >= 0.44: self.reading = 5
            elif percent >= 0.29: self.reading = 4
            else: self.reading = 3 if self.reading_corrects > 0 else 0

        return self

class TestResultDetail(TestResultRead):
    option_answers: List[OptionAnswerRead] = Field([], description="Detailed record of question-by-question answers")

class TestResultRequest(BaseModel):
    test_id: int = Field(..., description="The ID of the test to analyze", examples=[1])
    name: str = Field(..., description="The name of the test for identification", examples=["CELPIP Test 1"])
