"""Day 4 / Task 3 - streaming, retry policies, parallel fan-out/fan-in, subgraphs, visualization (offline demo)."""
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from Week8.exceptions import PermanentError, TransientError

def merge_dicts(a: dict, b: dict) -> dict:
    return {**(a or {}), **(b or {})}

# ---------- 1) Retry policy: retry TRANSIENT errors only ----------
class RState(TypedDict):
    value: str

CALLS = {"n": 0}

def flaky_api(state: RState) -> dict:
    CALLS["n"] += 1
    if CALLS["n"] < 3:
        raise TransientError(f"timeout on call {CALLS['n']}")
    return {"value": "ok after retries"}

def broken_logic(state: RState) -> dict:
    raise PermanentError("bad input - retrying will not help")

def demo_retry():
    policy = RetryPolicy(max_attempts=4, initial_interval=0.1, backoff_factor=2.0, retry_on=TransientError)
    b = StateGraph(RState)
    b.add_node("flaky_api", flaky_api, retry_policy=policy)
    b.add_edge(START, "flaky_api")
    b.add_edge("flaky_api", END)
    print("transient:", b.compile().invoke({"value": ""}), "| calls:", CALLS["n"])

    b2 = StateGraph(RState)
    b2.add_node("broken", broken_logic, retry_policy=policy)
    b2.add_edge(START, "broken")
    b2.add_edge("broken", END)
    try:
        b2.compile().invoke({"value": ""})
    except PermanentError as e:
        print("permanent failure surfaced immediately:", e)

# ---------- 2) Parallel fan-out / fan-in ----------
class PState(TypedDict):
    text: str
    results: Annotated[dict, merge_dicts]  # reducer merges concurrent writes
    report: str

def sentiment(s: PState) -> dict:
    pos = sum(w in s["text"].lower() for w in ("great", "good", "love"))
    neg = sum(w in s["text"].lower() for w in ("bad", "poor", "hate"))
    return {"results": {"sentiment": "positive" if pos > neg else "negative" if neg > pos else "neutral"}}

def length(s: PState) -> dict:
    return {"results": {"words": len(s["text"].split())}}

def shouting(s: PState) -> dict:
    return {"results": {"shouting": s["text"].isupper()}}

def join(s: PState) -> dict:
    return {"report": ", ".join(f"{k}={v}" for k, v in sorted(s["results"].items()))}

def build_parallel():
    b = StateGraph(PState)
    for n, f in [("sentiment", sentiment), ("length", length), ("shouting", shouting), ("join", join)]:
        b.add_node(n, f)
    for n in ("sentiment", "length", "shouting"):
        b.add_edge(START, n)           # fan-out: all three run in the same step
    b.add_edge(["sentiment", "length", "shouting"], "join")  # fan-in: wait for ALL three
    b.add_edge("join", END)
    return b.compile()

# ---------- 3) Subgraph used as a node ----------
class SubState(TypedDict):
    text: str

def strip_ws(s: SubState) -> dict:
    return {"text": " ".join(s["text"].split())}

def lower(s: SubState) -> dict:
    return {"text": s["text"].lower()}

def build_normalizer():
    sb = StateGraph(SubState)
    sb.add_node("strip_ws", strip_ws)
    sb.add_node("lower", lower)
    sb.add_edge(START, "strip_ws")
    sb.add_edge("strip_ws", "lower")
    sb.add_edge("lower", END)
    return sb.compile()

def build_with_subgraph():
    b = StateGraph(PState)
    b.add_node("normalize", build_normalizer())  # shared key `text` flows in and out
    b.add_node("analyze", build_parallel())
    b.add_edge(START, "normalize")
    b.add_edge("normalize", "analyze")
    b.add_edge("analyze", END)
    return b.compile()

def main():
    print("== retry ==")
    demo_retry()

    print("\n== parallel + streaming ==")
    graph = build_parallel()
    for update in graph.stream({"text": "I love this GREAT product", "results": {}}, stream_mode="updates"):
        print(update)

    print("\n== subgraph ==")
    print(build_with_subgraph().invoke({"text": "   I HATE   this BAD   thing  ", "results": {}}))

    print("\n== mermaid diagram (paste into https://mermaid.live) ==")
    print(build_parallel().get_graph().draw_mermaid())

if __name__ == "__main__":
    main()
