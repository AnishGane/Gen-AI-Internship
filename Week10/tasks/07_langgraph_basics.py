"""Day 3 / Task 1 - the smallest useful StateGraph (no LLM needed)."""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    text: str
    word_count: int
    shout: str

def count_words(state: State) -> dict:
    return {"word_count": len(state["text"].split())}  # nodes return PARTIAL updates

def shout(state: State) -> dict:
    return {"shout": state["text"].upper() + "!"}

def build_graph():
    builder = StateGraph(State)
    builder.add_node("count_words", count_words)
    builder.add_node("shout", shout)
    builder.add_edge(START, "count_words")
    builder.add_edge("count_words", "shout")
    builder.add_edge("shout", END)
    return builder.compile()  # compile = validate + make runnable

if __name__ == "__main__":
    graph = build_graph()
    print(graph.invoke({"text": "hello langgraph world"}))
    print(graph.get_graph().draw_mermaid())
