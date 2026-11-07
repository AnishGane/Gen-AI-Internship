"""Central configuration. Values come from environment / .env."""

import os
from dotenv import load_dotenv
from dataclasses import dataclass
from Week7.exceptions import ConfigError

load_dotenv()

def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError as e:
        raise ConfigError(f"{name} must be an integer") from e

@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY")
    base_url: str = os.getenv("BASE_URL")
    llm_model: str = os.getenv("LLM_MODEL")
    llm_max_tokens: int = _int("LLM_MAX_TOKENS", 400)
    llm_timeout_s: int = _int("LLM_TIMEOUT_S", 60)
    llm_max_retries: int = _int("LLM_MAX_RETRIES", 3)
    qdrant_path: str = os.getenv("QDRANT_PATH")
    collection_name: str = os.getenv("COLLECTION_NAME")
    dense_model: str = os.getenv("DENSE_MODEL")
    dense_dim: int = _int("DENSE_DIM", 384)
    sparse_model: str = os.getenv("SPARSE_MODEL")
    rerank_model: str = os.getenv("RERANK_MODEL")
    top_k: int = _int("TOP_K", 5)
    chunk_size: int = _int("CHUNK_SIZE", 100)
    chunk_overlap: int = _int("CHUNK_OVERLAP", 20)
    context_token_budget: int = _int("CONTEXT_TOKEN_BUDGET", 3000)
    max_upload_mb: int = _int("MAX_UPLOAD_MB", 20)
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    def validate_for_llm(self) -> None:
        if not self.openrouter_api_key:
            raise ConfigError("OPENROUTER_API_KEY is required")
        if self.chunk_overlap >= self.chunk_size:
            raise ConfigError("CHUNK_OVERLAP must be less than CHUNK_SIZE")
        if self.context_token_budget <= 0:
            raise ConfigError("CONTEXT_TOKEN_BUDGET must be greater than 0")
        if self.max_upload_mb <= 0:
            raise ConfigError("MAX_UPLOAD_MB must be greater than 0")
        if self.qdrant_url is None:
            raise ConfigError("QDRANT_URL is required")

    def validate_for_dense(self) -> None:
        if not self.dense_model:
            raise ConfigError("DENSE_MODEL is required")

    def validate_for_rerank(self) -> None:
        if not self.rerank_model:
            raise ConfigError("RERANK_MODEL is required")

    def validate_for_qdrant(self) -> None:
        if not self.qdrant_url:
            raise ConfigError("QDRANT_URL is required")

    def validate_for_collection(self) -> None:
        if not self.collection_name:
            raise ConfigError("COLLECTION_NAME is required")

    def validate_for_upload(self) -> None:
        if self.max_upload_mb <= 0:
            raise ConfigError("MAX_UPLOAD_MB must be greater than 0")

settings = Settings()