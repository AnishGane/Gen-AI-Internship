import uuid
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class Extracted_info(BaseModel):
    title: str = Field(description="A short title for the text")
    summary: str = Field(description="Summary in at most 3 sentences")
    keywords: list[str] = Field(
        description="3 to 8 important keywords",
        min_length=3,
        max_length=8,
    )
    category: Literal[
        "technology", "business", "science", "health", "education", "other"
    ]

    @field_validator("keywords", mode="before")
    @classmethod
    def clean_keywords(cls, value: list[str]) -> list[str]:
        cleaned = [keyword.strip().lower() for keyword in value if keyword.strip()]

        if len(cleaned) < 3:
            raise ValueError("At least 3 non-blank keywords are required")

        return cleaned

class QueryRoute(BaseModel):
    route: Literal["general", "math", "technical"]
    reason: str = Field(description="One short sentence explaining the choice")

class MathExpression(BaseModel):
    expression: str = Field(description="A plain arithmetic expression, e.g. '(12 + 8) * 3'")

class RagRoute(BaseModel):
    route: Literal["general", "knowledge"]

class RelevanceGrade(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="0 = irrelevant, 1 = fully answers the question")
    relevant: bool
    reason: str

class GroundedAnswer(BaseModel):
    answer: str
    citations: list[int] = Field(default_factory=list, description="Numbers of passages used, e.g. [1, 3]")
    sufficient_evidence: bool = Field(description="False if the passages do not contain the answer")

class Faithfulness(BaseModel):
    faithful: bool = Field(description="True if every claim in the answer is supported by the passages")
    reason: str

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    @field_validator("question", mode="before")
    @classmethod
    def strip_question(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

class Source(BaseModel):
    id: int
    source: str
    snippet: str
    score: float | None = None

class ChatResponse(BaseModel):
    thread_id: str
    answer: str
    status: Literal["general", "answered", "fallback"]
    route: str
    sources: list[Source] = []
    attempts: int = 0
    rewrites: list[str] = []
    latency_ms: int = 0