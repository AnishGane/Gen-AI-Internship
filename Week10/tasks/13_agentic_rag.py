"""Day 5 / Task 1 - basic Agentic RAG: classify -> retrieve -> grounded answer (with citations) -> fallback.
"""
import json

from Week10.RAG.workflow import ask, build_rag_graph, summarize

QUESTIONS = [
    "Hello! Can you give me a one-line motivational quote?",           # general
    "What is a checkpointer in LangGraph and why do I need a thread_id?",  # knowledge + citations
    "What is the warranty period of the Zorblax 9000 blender?",        # not in KB -> insufficient evidence
]

if __name__ == "__main__":
    graph = build_rag_graph(adaptive=False)  # no grading/rewriting yet - Task 2 adds it
    for i, q in enumerate(QUESTIONS):
        out = summarize(ask(graph, q, thread_id=f"day5-basic-{i}"))
        print(f"\nQ: {q}\n{json.dumps(out, indent=2, ensure_ascii=False)}")
