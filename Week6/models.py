from pydantic import BaseModel, Field

class DocumentChunk(BaseModel):
    """
    A chunk of text extracted from a document.
    """
    text: str = Field(min_length = 1)
    source: str = Field(min_length = 1)
    chunk_id: int = Field(ge=0)

class EmbeddedChunk(BaseModel):
    """
    Represents the document chunk with its embedding.
    """

    text: str = Field(min_length = 1)
    source: str = Field(min_length = 1)
    chunk_id: int = Field(ge=0)
    vector: list[float]

    def to_payload(self) -> dict:
        return {
            "text": self.text,
            "source": self.source,
            "chunk_id": self.chunk_id,
        }

class SearchChunk(BaseModel):
    """
    Represents a vector search result.
    """

    text: str
    source: str
    chunk_id: int
    score: float