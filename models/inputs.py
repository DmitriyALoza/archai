from pydantic import BaseModel, Field
from typing import Optional


class UserInput(BaseModel):
    raw_idea: str = Field(..., description="The user's raw system idea")
    context: Optional[str] = Field(None, description="Additional context or constraints")


class ClarificationAnswer(BaseModel):
    question: str = Field(..., description="The clarifying question that was asked")
    answer: str = Field(..., description="The user's answer to the question")


class ClarificationAnswers(BaseModel):
    answers: list[ClarificationAnswer] = Field(default_factory=list)
