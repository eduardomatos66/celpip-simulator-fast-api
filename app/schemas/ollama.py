from typing import Optional
from pydantic import BaseModel, Field

class OllamaRequest(BaseModel):
    model: str = "llama3"
    prompt: str
    stream: bool = False

class CLBScore(BaseModel):
    gradeCLB: Optional[int] = Field(default=None, alias="gradeCLB")

class WritingEvaluation(BaseModel):
    generalAverageCLB: Optional[CLBScore] = Field(default=None, alias="generalAverageCLB")
    # Additional fields can be mapped here as the original Java 'WritingEvaluation' had more structure
    # like vocabulary, grammar, etc.
    raw_response: Optional[str] = None
