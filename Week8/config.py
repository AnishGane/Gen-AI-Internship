
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    api_key: str = os.getenv("OPENROUTER_API_KEY")
    index_path: str = ".rag_index"
    collection_name: str = "documents"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chat_model: str = "openrouter/free"
    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 5
    max_cosine_distance: float = 0.75

    def __post_init__(self) -> None:
        if not self.api_key.strip():
            raise ValueError("An OpenRouter API key is required.")
        if self.chunk_size is None:
            object.__setattr__(self, "chunk_size", 800)
        if self.chunk_overlap is None:
            object.__setattr__(self, "chunk_overlap", 120)
        if not isinstance(self.chunk_size, int) or not isinstance(self.chunk_overlap, int):
            raise ValueError("chunk_size and chunk_overlap must be whole numbers.")
        if self.chunk_size <= 0 or not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError("Chunk overlap must be non-negative and smaller than chunk size.")
        if self.top_k < 1:
            raise ValueError("top_k must be at least 1.")
        if not 0 <= self.max_cosine_distance <= 2:
            raise ValueError("max_cosine_distance must be between 0 and 2.")