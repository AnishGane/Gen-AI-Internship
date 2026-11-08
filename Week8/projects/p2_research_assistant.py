"""PROJECT 2 - Research assistant with map-reduce (LangGraph Send API).

question -> plan sub-questions -> [parallel: retrieve + summarise each] -> synthesize a cited report
Run:  python -m projects.p2_research_assistant "Compare LangChain agents and LangGraph workflows"
"""
import operator
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field

from Week8.core.llm import get_llm
from Week8.RAG.evaluator import format_context
from Week8.RAG.retriever import retrieve_chunks

class Plan(BaseModel):
    sub_questions: list[str] = Field(min_length=2, max_length=4)

class State(TypedDict, total=False):
    question: str
    sub_questions: list[str]
    findings: Annotated[list[dict], operator.add]  # parallel branches append here
    report: str

def plan_node(s: State) -> dict:
    p = get_llm().with_structured_output(Plan, method="function_calling").invoke(
        f"Break this research question into 2-4 focused sub-questions answerable from a technical knowledge base:\n{s['question']}")
    return {"sub_questions": p.sub_questions}

def fan_out(s: State):
    # One Send per sub-question -> one parallel `research` run each
    return [Send("research", {"sub_question": q}) for q in s["sub_questions"]]

def research_node(payload: dict) -> dict:  # receives the Send payload, not the full state
    q = payload["sub_question"]
    chunks = retrieve_chunks(q, k=3)
    summary = get_llm().invoke(
        f"Using ONLY these passages, answer briefly (cite like [1]). Say 'no evidence' if absent.\n"
        f"{format_context(chunks)}\n\nQuestion: {q}").content
    return {"findings": [{"question": q, "summary": summary, "sources": sorted({c['source'] for c in chunks})}]}

def synthesize_node(s: State) -> dict:
    notes = "\n\n".join(f"Q: {f['question']}\nA: {f['summary']}\nSources: {f['sources']}" for f in s["findings"])
    report = get_llm(temp=0.2).invoke(
        f"Write a structured research report (short sections, bullet points) answering: {s['question']}\n"
        f"Use only these findings and keep source file names.\n\n{notes}").content
    return {"report": report}

def build_graph():
    b = StateGraph(State)
    b.add_node("plan", plan_node)
    b.add_node("research", research_node)
    b.add_node("synthesize", synthesize_node)
    b.add_edge(START, "plan")
    b.add_conditional_edges("plan", fan_out, ["research"])
    b.add_edge("research", "synthesize")
    b.add_edge("synthesize", END)
    return b.compile()

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "Compare LangChain agents and LangGraph workflows, and explain how persistence works"
    print(build_graph().invoke({"question": q, "findings": []})["report"])
