"""Day 5 / Task 3 - serve the API, tracing, and evaluation.

  uv run .\Week8\tasks\15_rag_api_and_evaluation.py serve                 # FastAPI on :8000
  uv run .\Week8\tasks\15_rag_api_and_evaluation.py eval [--judge]        # local evaluation over data/eval_set.json
  uv run .\Week8\tasks\15_rag_api_and_evaluation.py langsmith             # push dataset + run a LangSmith experiment

TRACING: set LANGSMITH_TRACING=true, LANGSMITH_API_KEY, LANGSMITH_PROJECT in .env. Every graph run (nodes,
model calls, tools, latency, tokens) then appears in LangSmith - no code changes needed.
"""
import json
import statistics
import sys
import time
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from Week8.core.llm import get_llm
from Week8.core.prompts import JUDGE_PROMPT
from Week8.lg.memory import get_checkpointer
from Week8.models import Faithfulness
from Week8.RAG.workflow import ask, build_rag_graph, summarize

EVAL_PATH = PROJECT_ROOT / "data" / "eval_set.json"

def judge_faithfulness(answer: str, sources: list[dict]) -> bool:
    ctx = "\n\n".join(f"[{s['id']}] {s['snippet']}" for s in sources)
    judge = get_llm().with_structured_output(Faithfulness, method="function_calling")
    return judge.invoke(JUDGE_PROMPT.format_messages(context=ctx, answer=answer)).faithful

def run_case(graph, case: dict, use_judge: bool) -> dict:
    t0 = time.perf_counter()
    out = summarize(ask(graph, case["question"], f"eval-{uuid.uuid4()}", {"tags": ["week8", "eval"]}))
    res = {"question": case["question"], "latency_s": time.perf_counter() - t0, "status": out["status"],
           "attempts": out["attempts"], "route_ok": out["route"] == case["route"]}
    if case.get("should_fallback"):
        res["fallback_ok"] = out["status"] == "fallback"
    elif case["route"] == "knowledge":
        res["retrieval_hit"] = any(case["expected_source"] in s["source"] for s in out["sources"])
        ans = out["answer"].lower()
        kws = case.get("expected_keywords", [])
        res["keyword_recall"] = sum(k in ans for k in kws) / len(kws) if kws else None
        res["has_citation"] = bool(out["sources"])
        if use_judge and out["sources"]:
            res["faithful"] = judge_faithfulness(out["answer"], out["sources"])
    return res

def run_eval(use_judge: bool = False):
    graph = build_rag_graph(checkpointer=get_checkpointer("memory"), adaptive=True)
    results = [run_case(graph, c, use_judge) for c in json.loads(EVAL_PATH.read_text(encoding="utf-8"))]
    for r in results:
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})

    def rate(key):
        vals = [r[key] for r in results if r.get(key) is not None]
        return f"{sum(vals)}/{len(vals)}" if vals else "n/a"

    print("\n=== SUMMARY ===")
    for key in ("route_ok", "retrieval_hit", "has_citation", "fallback_ok", "faithful"):
        print(f"{key:15s}: {rate(key)}")
    kr = [r["keyword_recall"] for r in results if r.get("keyword_recall") is not None]
    print(f"{'keyword_recall':15s}: {statistics.mean(kr):.2f}" if kr else "")
    lat = sorted(r["latency_s"] for r in results)
    print(f"latency  mean={statistics.mean(lat):.1f}s  max={lat[-1]:.1f}s")

def run_langsmith():
    from langsmith import Client, evaluate

    client, name = Client(), "week8-agentic-rag-eval"
    cases = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    if not client.has_dataset(dataset_name=name):
        ds = client.create_dataset(name)
        client.create_examples(dataset_id=ds.id, inputs=[{"question": c["question"]} for c in cases],
                               outputs=[{k: v for k, v in c.items() if k != "question"} for c in cases])
    graph = build_rag_graph(checkpointer=get_checkpointer("memory"), adaptive=True)

    def target(inputs: dict) -> dict:
        return summarize(ask(graph, inputs["question"], f"ls-{uuid.uuid4()}"))

    def route_correct(outputs: dict, reference_outputs: dict) -> dict:
        return {"key": "route_correct", "score": float(outputs["route"] == reference_outputs["route"])}

    def cited_when_expected(outputs: dict, reference_outputs: dict) -> dict:
        if reference_outputs.get("should_fallback") or reference_outputs["route"] == "general":
            return {"key": "citation_ok", "score": float(not outputs["sources"])}
        return {"key": "citation_ok", "score": float(bool(outputs["sources"]))}

    evaluate(target, data=name, evaluators=[route_correct, cited_when_expected], experiment_prefix="agentic-rag")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "eval"
    if cmd == "serve":
        import uvicorn

        uvicorn.run("app:app", host="127.0.0.1", port=8000)
    elif cmd == "langsmith":
        run_langsmith()
    else:
        run_eval(use_judge="--judge" in sys.argv)
