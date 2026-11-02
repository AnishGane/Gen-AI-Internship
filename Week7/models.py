from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field


class Chunk(BaseModel):
    point_id: str
    document_id: str
    source: str
    chunk_id: str
    chunk_index: int
    page: int | None = None
    section: str | None = None
    text: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class RetrievedChunk(BaseModel):
    point_id: str
    score: float
    text: str
    document_id: str
    source: str
    chunk_id: str
    chunk_index: int = 0
    page: int | None = None
    section: str | None = None
    rerank_score: float | None = None

class Answer(BaseModel):
    answer: str
    citations: list[str] = []
    confidence: Literal["high", "medium", "low"] = "low"
    insufficient_evidence: bool = False
