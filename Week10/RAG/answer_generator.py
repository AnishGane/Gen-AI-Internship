"""Grounded answer generation with numbered citations."""

from Week10.RAG.evaluator import format_context
from Week10.core.prompts import GROUNDED_ANSWER_PROMPT
from Week10.core.llm import get_llm
from Week10.models import GroundedAnswer

def generate_grounded_answer(question: str, chunks: list[dict]) -> GroundedAnswer:
    llm = get_llm().with_structured_output(GroundedAnswer, method="function_calling")
    return llm.invoke(GROUNDED_ANSWER_PROMPT.format(context=format_context(chunks), question = question))

def build_sources(chunks: list[dict], cited: list[int]) -> list[dict]:
    """Map the model's cited passage numbers back to real chunks (ignores invalid numbers)."""
    sources = []
    for n in sorted(set(cited)):
        if 1 <= n <= len(chunks):
            c = chunks[n - 1]
            sources.append({"id": n, "source": c["source"], "snippet": c["content"][:300], "score": c.get("score")})
    return sources