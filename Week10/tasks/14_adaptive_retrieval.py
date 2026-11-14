"""Day 5 / Task 2 - adaptive retrieval: grade -> rewrite -> retry (bounded) -> fallback, plus a persisted conversation."""
import json

from Week10.lg.memory import get_checkpointer
from Week10.RAG.workflow import ask, build_rag_graph, summarize

def show(title: str, q: str, out: dict):
    print(f"\n=== {title}\nQ: {q}\n{json.dumps(summarize(out), indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    graph = build_rag_graph(checkpointer=get_checkpointer(), adaptive=True)

    cases = [
        ("General question", "Hi! What's a good name for a pet goldfish?"),
        ("Knowledge + citations", "What does Qdrant need me to keep consistent between indexing and querying?"),
        # Vague / jargon-free wording -> first retrieval may be weak -> watch `rewrites`
        ("Weak retrieval -> rewrite", "how do i make the bot pause and wait for a person to say ok"),
        ("Insufficient evidence", "What is the warranty period of the Zorblax 9000 blender?"),
    ]
    for i, (title, q) in enumerate(cases):
        show(title, q, ask(graph, q, thread_id=f"day5-adaptive-{i}"))

    # Persisted conversation: SAME thread_id => the general route sees earlier turns
    print("\n=== Persisted conversation (thread 'chat-42')")
    ask(graph, "Please remember my favourite colour is teal.", "chat-42")
    out = ask(graph, "What is my favourite colour?", "chat-42")
    print("A:", out["answer"])
    print("messages stored in thread:", len(graph.get_state({"configurable": {"thread_id": "chat-42"}}).values["messages"]))
