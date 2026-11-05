"""Day 2 + 6: standalone-question rewriting (history-aware) and multi-query expansion."""
import json
from Week7.core.generation.llm_service import LLMService

REWRITE_SYS = ("Rewrite the user's latest question as a standalone search query, resolving pronouns "
               "using the chat history. Return ONLY the rewritten query.")
MULTI_SYS = ("Generate {n} diverse search queries (different wording/angles) for the question. "
             'Return ONLY a JSON array of strings.')

class QueryRewriter:
    def __init__(self, llm: LLMService):
        self.llm = llm

    def rewrite(self, question: str, history: list[dict]) -> str:
        if not history:
            return question
        hist = "\n".join(f"{m['role']}: {m['content']}" for m in history[-6:])
        out = self.llm.complete(REWRITE_SYS, f"History:\n{hist}\n\nLatest question: {question}", max_tokens=150)
        return out.strip().strip('"') or question

    def expand(self, question: str, n: int = 3) -> list[str]:
        try:
            raw = self.llm.complete(MULTI_SYS.format(n=n), question, max_tokens=300)
            qs = json.loads(raw[raw.find("["): raw.rfind("]") + 1])
            return [question] + [q for q in qs if isinstance(q, str) and q != question][:n]
        except Exception:
            return [question]
