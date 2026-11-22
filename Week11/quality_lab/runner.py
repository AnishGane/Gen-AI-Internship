from __future__ import annotations

import subprocess
import sys
import time
import uuid
from unittest.mock import patch
from Week11.quality_lab.config import CASES_PATH, REPO_ROOT, Runner, VARIANTS
from Week11.quality_lab.data import load_jsonl, redact

def git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"

def inferred_path(state: dict) -> str:
    """Infer likely graph nodes from final state; this is not a LangSmith trace."""
    path = ["prepare", "classify"]
    if state.get("route") == "general":
        return " > ".join([*path, "general_answer"])
    attempts = max(int(state.get("attempts", 0) or 0), 1)
    for index in range(attempts):
        path += ["retrieve", "grade"]
        if index < attempts - 1:
            path.append("rewrite")
    if state.get("status") == "fallback":
        if state.get("relevance", 0.0) >= 0.6:
            path.append("generate")
        path.append("fallback")
    else:
        path.append("generate")
    return " > ".join(path)

def make_runner(variant: str) -> tuple[Runner, dict]:
    """Build a runner around the real Week 10 LangGraph application."""
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant}")
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from langchain_core.tracers.context import collect_runs
    import Week10.RAG.workflow as workflow
    from Week10.config import settings
    from Week10.lg.memory import get_checkpointer

    graph = workflow.build_rag_graph(checkpointer=get_checkpointer("memory"), adaptive=True)
    baseline_k = settings.top_k
    top_k = VARIANTS[variant]["top_k"] or baseline_k
    original_retrieve = workflow.retrieve_chunks
    info = {
        "model_id": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "top_k": top_k,
        "baseline_top_k": baseline_k,
        "relevance_threshold": settings.relevance_threshold,
        "max_retries": settings.max_retries,
        "collection": settings.collection_name,
    }

    def runner(question: str, inject_chunk: dict | None = None, case_id: str = "adhoc") -> dict:
        def patched_retrieve(query: str, k_: int | None = None):
            chunks = original_retrieve(query, k=top_k)
            if inject_chunk:
                chunks = [{
                    "content": inject_chunk["content"], "source": inject_chunk["source"], "score": 0.99,
                }, *chunks]
            return chunks

        started = time.perf_counter()
        with patch.object(workflow, "retrieve_chunks", patched_retrieve), collect_runs() as callback:
            state = workflow.ask(
                graph, question, f"eval-{uuid.uuid4()}",
                {"run_name": f"eval_{case_id}", "tags": ["week11", "eval", variant],
                 "metadata": {"case_id": case_id, "variant": variant}},
            )
        root = callback.traced_runs[0] if callback.traced_runs else None
        return {
            "answer": state.get("answer", ""), "status": state.get("status", ""),
            "route": state.get("route", ""), "sources": state.get("sources", []),
            "documents": state.get("documents", []), "attempts": state.get("attempts", 0),
            "rewrites": state.get("rewrites", []), "relevance": state.get("relevance", 0.0),
            "latency_s": time.perf_counter() - started, "node_path": inferred_path(state),
            "run_id": str(root.id) if root else None,
        }

    return runner, info

def make_mock_runner(bad_ids: set[str] | None = None) -> Runner:
    """Offline stand-in for testing harness plumbing; it does not assess model quality."""
    bad_ids = bad_ids or set()
    cases = {case["question"]: case for case in load_jsonl(CASES_PATH)}

    def runner(question: str, inject_chunk: dict | None = None, case_id: str = "adhoc") -> dict:
        case = cases.get(question)
        base = {
            "documents": [], "sources": [], "attempts": 1, "rewrites": [], "relevance": 0.9,
            "latency_s": 0.01, "node_path": "mock", "run_id": None,
        }
        if case is None:
            return {
                **base, "answer": "I couldn't find enough reliable information in the knowledge base.",
                "status": "fallback", "route": "knowledge",
            }
        if case_id in bad_ids:
            return {**base, "answer": "Totally made up answer.", "status": "answered", "route": "knowledge"}
        status = case["expected_status_any"][0]
        if status != "answered":
            answer = "I couldn't find enough reliable information." if status == "fallback" else "Hello!"
            route = case.get("expected_route", "knowledge" if status == "fallback" else "general")
            return {**base, "answer": answer, "status": status, "route": route}

        terms = case.get("expected_contains_all") or case.get("expected_contains_any") or []
        names = case.get("expected_sources", [])
        documents = [
            {"content": f"{' '.join(terms)} (from {name})", "source": name, "score": 0.9}
            for name in names
        ] or [{"content": " ".join(terms), "source": "mock.md", "score": 0.9}]
        sources = [
            {"id": index, "source": document["source"], "snippet": document["content"], "score": 0.9}
            for index, document in enumerate(documents, 1)
        ]
        return {
            **base, "answer": " ".join(terms), "status": "answered", "route": "knowledge",
            "documents": documents, "sources": sources,
        }

    return runner

def call_with_retry(runner: Runner, retries: int, **kwargs) -> dict:
    """Retry transient failures; preserve final failures as errors rather than quality misses."""
    last_error = ""
    for attempt in range(retries + 1):
        try:
            return runner(**kwargs)
        except Exception as exc:  # A failed call is part of the run record.
            last_error = f"{type(exc).__name__}: {exc}"
            transient = any(token in last_error.lower() for token in ("429", "rate limit", "timeout", "temporarily", "503"))
            if attempt < retries and transient:
                time.sleep(2 ** attempt * 3)
                continue
            break
    return {
        "error": redact(last_error)[:500], "answer": "", "status": "error", "route": "",
        "sources": [], "documents": [], "latency_s": 0.0,
    }