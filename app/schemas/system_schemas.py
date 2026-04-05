from typing import Dict
from pydantic import BaseModel, Field

class DiskUsage(BaseModel):
    total: float = Field(..., description="Total disk space in GB")
    used: float = Field(..., description="Used disk space in GB")
    free: float = Field(..., description="Free disk space in GB")
    percent: float = Field(..., description="Percentage of disk space used")

class SystemHealth(BaseModel):
    status: str = Field(..., description="Overall system status")
    database_connected: bool = Field(..., description="Status of the database connection")
    disk_usage: DiskUsage
    uptime_seconds: float = Field(..., description="Application uptime in seconds")
    uptime_human: str = Field(..., description="Human-readable uptime")

class SystemStats(BaseModel):
    total_answers_sheets: int = Field(..., description="Total number of answer sheets in the database")
    total_questions: int = Field(..., description="Total number of questions in the database")
    questions_per_area: Dict[str, int] = Field(..., description="Number of questions grouped by test area (e.g., listening, reading)")
