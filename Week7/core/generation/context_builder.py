"""Day 3: dedupe -> (optional) compress -> token budget -> order -> labelled sources [S1]..."""
import re
from dataclasses import dataclass, field
from Week7.models import RetrievedChunk

def approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))

def dedupe(chunks: list[RetrievedChunk], threshold: float = 0.85) -> list[RetrievedChunk]:
    kept: list[RetrievedChunk] = []
    for c in chunks:
        t = _tokens(c.text)
        dup = any(len(t & _tokens(k.text)) / max(len(t | _tokens(k.text)), 1) >= threshold for k in kept)
        if not dup and all(c.point_id != k.point_id for k in kept):
            kept.append(c)
    return kept

def compress(chunk_text: str, query: str, min_keep: int = 2) -> str:
    """Cheap extractive compression: keep sentences sharing terms with the query."""
    sents = re.split(r"(?<=[.!?])\s+", chunk_text)
    q = _tokens(query) - {"the", "a", "of", "to", "is", "in", "and", "what", "how", "for"}
    keep = [s for s in sents if q & _tokens(s)]
    return " ".join(keep) if len(keep) >= min_keep else chunk_text

@dataclass
class BuiltContext:
    text: str
    sources: dict[str, RetrievedChunk] = field(default_factory=dict)  # "S1" -> chunk

    @property
    def source_ids(self) -> set[str]:
        return set(self.sources)
        
class ContextBuilder:
    def __init__(self, token_budget: int = 3000, order: str = "score", use_compression: bool = False):
        self.token_budget, self.order, self.use_compression = token_budget, order, use_compression

    def build(self, query: str, chunks: list[RetrievedChunk]) -> BuiltContext:
        chunks = dedupe(chunks)
        selected, used = [], 0
        for c in chunks:  # chunks arrive best-first
            body = compress(c.text, query) if self.use_compression else c.text
            cost = approx_tokens(body) + 20
            if used + cost > self.token_budget:
                continue
            selected.append((c, body)); used += cost
        if self.order == "document":   # reading order inside each doc
            selected.sort(key=lambda x: (x[0].document_id, x[0].chunk_index))
        elif self.order == "edges":    # lost-in-the-middle: best at start AND end
            front, back = selected[0::2], selected[1::2][::-1]
            selected = front + back
        sources, parts = {}, []
        for i, (c, body) in enumerate(selected, 1):
            sid = f"S{i}"
            sources[sid] = c
            loc = f"{c.source}" + (f", p.{c.page}" if c.page else "") + (f", section: {c.section}" if c.section else "")
            parts.append(f'<source id="{sid}" chunk_id="{c.chunk_id}" from="{loc}">\n{body}\n</source>')
        return BuiltContext(text="\n\n".join(parts), sources=sources)