"""Day 6: Recall@K, Precision@K, MRR over a golden dataset (document-level relevance)."""
from typing import Callable
from Week7.models import RetrievedChunk

def recall_at_k(retrieved: list[str], relevant: set[str], k: int) ->float:
     return len(set(retrieved[:k]) & relevant) / len(relevant) if relevant else 0.0

def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    top = retrieved[:k]
    return sum(1 for r in top if r in relevant) / k if k else 0.0

def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    for i, r in enumerate(retrieved, 1):
        if r in relevant:
            return 1 / i
    return 0.0

def evaluate_retrieval(dataset: list[dict], retrieve_fn: Callable[[str], list[RetrievedChunk]],
                       ks=(1, 3, 5)) -> dict:
    """dataset item: {question, relevant_sources: [filename,...], answerable: bool}
    Uses `source` (filename) so the dataset survives re-chunking."""
    rows = [d for d in dataset if d.get("answerable", True) and d.get("relevant_sources")]
    agg = {f"recall@{k}": 0.0 for k in ks} | {f"precision@{k}": 0.0 for k in ks} | {"mrr": 0.0}
    for d in rows:
        got = list(dict.fromkeys(
            chunk.source for chunk in retrieve_fn(d["question"])
        ))
        rel = set(d["relevant_sources"])
        for k in ks:
            agg[f"recall@{k}"] += recall_at_k(got, rel, k)
            agg[f"precision@{k}"] += precision_at_k(got, rel, k)
        agg["mrr"] += reciprocal_rank(got, rel)
    n = max(len(rows), 1)
    return {k: round(v / n, 3) for k, v in agg.items()} | {"n": len(rows)}