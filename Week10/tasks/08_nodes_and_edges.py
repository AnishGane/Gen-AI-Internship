"""Day 3 / Task 2 - several nodes, reducers, streaming each node's update."""
import operator
from typing import Annotated, TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    raw: str
    tokens: list[str]
    stats: dict
    # Reducer: updates to `log` are APPENDED (operator.add) instead of overwriting
    log: Annotated[list[str], operator.add]

def clean(state: State) -> dict:
    return {"raw": " ".join(state["raw"].split()).strip(), "log": ["clean"]}

def tokenize(state: State) -> dict:
    return {"tokens": state["raw"].lower().split(), "log": [f"tokenize ({len(state['raw'].split())} words)"]}

def analyze(state: State) -> dict:
    tokens = state["tokens"]
    stats = {"count": len(tokens), "unique": len(set(tokens)), "longest": max(tokens, key=len, default="")}
    return {"stats": stats, "log": ["analyze"]}

def build_graph():
    b = StateGraph(State)
    for name, fn in [("clean", clean), ("tokenize", tokenize), ("analyze", analyze)]:
        b.add_node(name, fn)
    b.add_edge(START, "clean")
    b.add_edge("clean", "tokenize")
    b.add_edge("tokenize", "analyze")
    b.add_edge("analyze", END)
    return b.compile()

if __name__ == "__main__":
    graph = build_graph()
    inp = {"raw": "  LangGraph   makes   agent   workflows   explicit  ", "log": []}
    print(graph.invoke(inp))
    print("\n-- streaming per-node updates --")
    for update in graph.stream(inp, stream_mode="updates"):
        print(update)
