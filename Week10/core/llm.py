from langchain_openrouter import ChatOpenRouter
from langchain_core.embeddings import Embeddings
from Week10.config import settings
from typing import Any

def get_llm(temp: float = 0.0, **kwargs: Any) -> ChatOpenRouter:
    settings.validate_for_llm()

    protected = {
        "model",
        "api_key",
        "base_url",
        "temperature",
        "timeout",
        "max_retries",
    }

    conflicts = protected.intersection(kwargs)

    if conflicts:
        raise ValueError(
            f"Cannot override protected parameters: {conflicts}"
        )

    return ChatOpenRouter(
        model=settings.llm_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=temp,
        timeout=60_000,
        max_retries=(
            settings.max_retries
            if settings.max_retries is not None
            else 3
        ),
        **kwargs
    )

def get_embeddings() -> Embeddings:

    settings.validate_for_llm()

    if settings.embedding_provider == "openrouter":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            check_embedding_ctx_length=False,
            chunk_size=1,
            max_retries=(
                settings.max_retries
                if settings.max_retries is not None
                else 3
            ),
        )

    elif settings.embedding_provider == "huggingface":
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
        )

    else:
        raise ValueError(
            f"Unsupported embedding provider: "
            f"{settings.embedding_provider}"
        )
