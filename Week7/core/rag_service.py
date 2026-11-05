"""Orchestrates: rewrite -> multi-query -> retrieve -> rerank -> context -> grounded answer."""

from dataclasses import dataclass
from Week7.config import settings
from Week7.logger import get_logger, log_event, timer
from Week7.core.vector_store import VectorStore
from Week7.core.ingestion.document_processor import DocumentProcessor
from Week7.core.generation.llm_service import LLMService
from Week7.exceptions import RAGError
from Week7.logger import get_logger, log_event, timer
from Week7.models import RetrievedChunk
from Week7.core.generation.context_builder import ContextBuilder
from Week7.core.generation.answer_generator import AnswerGenerator

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
        self.store = VectorStore()
        self.processor = DocumentProcessor(self.store)
        self.retriever = Retriever(self.store)
        self.reranker = Reranker()
        self._llm: LLMService | None = None
        self.memory = ConversationStore()

    @property
    def llm(self) -> LLMService:         # lazy so ingestion works without an API key
        if self._llm is None:
            self._llm = LLMService()
        return self._llm

     # --- documents ---
    def ingest(self, path): return self.processor.ingest(path)
    def delete(self, document_id): self.processor.delete(document_id)

     # --- retrieval only (used by evaluation) ---
    def retrieve(self, question: str, cfg: PipelineConfig, filters=None, history=None,
                 timings: dict | None = None) -> tuple[str, list[RetrievedChunk]]:
        timings = timings if timings is not None else {}
        if not question.strip():
            raise RAGError("Question is empty")
        query = question
        with timer(timings, "rewrite_ms"):
            if cfg.use_rewrite and history:
                query = QueryRewriter(self.llm).rewrite(question, history)
            queries = QueryRewriter(self.llm).expand(query) if cfg.use_multi_query else [query]
        with timer(timings, "retrieval_ms"):
            cands = self.retriever.retrieve(queries, cfg.mode, cfg.candidates, filters)
        if cfg.use_rerank:
            with timer(timings, "rerank_ms"):
                cands = self.reranker.rerank(query, cands, cfg.final_k, cfg.min_rerank_score)
        else:
            cands = cands[:cfg.final_k]
        return query, cands

    # --- full pipeline ---
    def ask(self, question: str, session_id: str = "default", cfg: PipelineConfig | None = None,
            filters: dict | None = None) -> dict:
        cfg, t = cfg or PipelineConfig(), {}
        history = self.memory.get(session_id)
        try:
            query, chunks = self.retrieve(question, cfg, filters, history, t)
            ctx = ContextBuilder(settings.context_token_budget, cfg.context_order,
                                 cfg.use_compression).build(query, chunks)
            hist_txt = ("<history>\n" + "\n".join(f"{m['role']}: {m['content']}" for m in history[-6:])
                        + "\n</history>\n\n") if history else ""
            before = dict(self.llm.usage)
            with timer(t, "generation_ms"):
                ans = AnswerGenerator(self.llm).generate(question, ctx, hist_txt)  # ORIGINAL question
            tokens = {k: self.llm.usage[k] - before[k] for k in ("input_tokens", "output_tokens")}
        except RAGError as e:
            log_event(log, "ask_failed", error=str(e), question=question)
            raise
        self.memory.add(session_id, "user", question)
        self.memory.add(session_id, "assistant", ans.answer)
        result = {
            "question": question, "search_query": query, "answer": ans.model_dump(),
            "sources": {sid: {"source": c.source, "page": c.page, "chunk_id": c.chunk_id,
                              "retrieval_score": round(c.score, 4),
                              "rerank_score": None if c.rerank_score is None else round(c.rerank_score, 4)}
                        for sid, c in ctx.sources.items()},
            "timings_ms": t, "tokens": tokens,
        }
        log_event(log, "ask_done", question=question, timings=t, tokens=tokens,
                  insufficient=ans.insufficient_evidence, n_sources=len(ctx.sources))
        return result