"""LLM-based relevance grader for retrieved chunks."""

from Week10.core.prompts import GRADER_PROMPT
from Week10.core.llm import get_llm
from Week10.models import RelevanceGrade

def format_context(chunk: list[dict]) -> str:
    return "\n\n".join(f"[{i}] ({c['source']}) {c['content']}" for i, c in enumerate(chunk, 1))

def grade_documents(question: str, chunks: list[dict]) -> RelevanceGrade:
    if not chunks:
        return RelevanceGrade(
            score = 0.0,
            relevant=False,
            reason="No documents were retrieved."
        )

    grader = get_llm().with_structured_output(RelevanceGrade, method="function_calling")
    return grader.invoke(GRADER_PROMPT.format_messages(question=question, context=format_context(chunks)))