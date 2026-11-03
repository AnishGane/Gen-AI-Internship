"""Orchestrates: rewrite -> multi-query -> retrieve -> rerank -> context -> grounded answer."""

from dataclasses import dataclass
from Week7.config import settings
from Week7.logger import get_logger, log_event, timer

log = get_logger("rag")

@dataclass
class PipelineConfig:
    mode: str = "hybrid"
    candidates: int = 20
    use_rewrite: bool = True
    use_multi_query: bool = False
    use_rerank: bool = True
    final_k: int = 5
    use_compression: bool = False
    context_order: str = "score"  # score | document | edges
    min_rerank_score: float | None = None

BASELINE = PipelineConfig(mode="dense", candidates=5, use_rewrite=False, use_rerank=False, final_k=5)  # Day-1 style

class ConversationStore:
    """History is stored separately from document knowledge."""
    def __init__(self):
        self._h: dict[str, list[dict]] = {}

    def get(self, sid):
        return self._h.get(sid, [])
    
    def add(self, sid, role, content):
        self._h.setdefault(sid, []).append({"role": role, "content": content})

    def clear(self, sid): 
        self._h.pop(sid, None)

class RAGService:
    def __init__(self):
        self.store = True