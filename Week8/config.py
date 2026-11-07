import os
from dotenv import load_dotenv
from dataclasses import dataclass
from Week8.exceptions import ConfigError

load_dotenv()

def _value(name: str, default: int | float) -> int | float:
    try:
        if isinstance(default, int):
            return int(os.getenv(name, default))
        return float(os.getenv(name, default))
    except ValueError as e:
        raise ConfigError(f"{name} must be an integer or float") from e

@dataclass(frozen=True)
class Settings:
    # llm via openrouter
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY")
    openrouter_base_url: str = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
    llm_model: str = os.getenv("LLM_MODEL","openrouter/free")

    # qdrant
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: str | None = os.getenv("QDRANT_API_KEY") or None
    collection_name: str = os.getenv("W8_COLLECTION_NAME", "")
    qdrant_content_key: str = os.getenv("QDRANT_CONTENT_KEY", "page_content")
    qdrant_vector_name: str = os.getenv("QDRANT_VECTOR_NAME", "")

    # Embeddings
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "openrouter")
    embedding_model: str = os.getenv("EMBEDDING_MODEL")

    # RAG Behaviour
    top_k: int = _value("TOP_K", 4)
    relevance_threshold: float =  _value("RELEVANCE_THRESHOLD", 0.6)
    max_retries:int = _value("LLM_MAX_RETRIES", 3)

    # Persistence
    checkpointer: str = os.getenv("CHECKPOINTER", "memory")
    checkpoint_db:str = os.getenv("CHECKPOINT_DB", "checkpoint.sqlite")

    def validate_for_llm(self) -> None:
        if not self.openrouter_api_key:
            raise ConfigError("OPENROUTER_API_KEY is required")
        if not self.openrouter_base_url:
            raise ConfigError("BASE_URL is required")
        if not self.llm_model:
            raise ConfigError("LLM_MODEL is required")

    def validate_for_qdrant(self) -> None:
            if not self.qdrant_url:
                raise ConfigError("QDRANT_URL is required")
            if not self.collection_name:
                raise ConfigError("W8_COLLECTION_NAME is required")
            if not self.qdrant_content_key:
                raise ConfigError("QDRANT_CONTENT_KEY is required")

    def validate_for_embeddings(self) -> None:
            if not self.embedding_provider:
                raise ConfigError("EMBEDDING_PROVIDER is required")
            if not self.embedding_model:
                raise ConfigError("EMBEDDING_MODEL is required")

    def validate_for_rag(self) -> None:
            if self.top_k <= 0:
                raise ConfigError("TOP_K must be greater than 0")
            if not 0 <= self.relevance_threshold <= 1:
                raise ConfigError("RELEVANCE_THRESHOLD must be between 0 and 1")
            if self.max_retries < 0:
                raise ConfigError("LLM_MAX_RETRIES cannot be negative")

    def validate_for_persistence(self) -> None:
            if self.checkpointer not in {"memory", "sqlite"}:
                raise ConfigError("CHECKPOINTER must be 'memory' or 'sqlite'")
            if self.checkpointer == "sqlite" and not self.checkpoint_db:
                raise ConfigError("CHECKPOINT_DB is required for the sqlite checkpointer")

settings = Settings()

