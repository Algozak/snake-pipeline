"""Request and response validation schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(min_length=8, max_length=128)


class ScoreCreate(BaseModel):
    score: int = Field(ge=0, le=1_000_000)


class ScoreResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    score: int
    created_at: datetime
