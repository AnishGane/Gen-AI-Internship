"""PROJECT 1 - Customer-support triage bot (LangChain structured output + LangGraph HITL).

ticket -> triage (category/urgency/sentiment) -> draft reply -> [needs review? -> human approve/edit] -> send
Run:  python -m projects.p1_support_triage
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Literal
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command, interrupt
from Week8.core.llm import get_llm
from Week8.lg.memory import get_checkpointer
from Week8.models import State, Triage

def triage_node(state: State) -> dict:
    t= get_llm().with_structured_output(Triage, method="function_calling").invoke(
        f"Triage this support ticket:\n{state['ticket']}"
    )

    return {
        "triage": t.model_dump()
    }

def draft_node(state: State) -> dict:
    msg = get_llm(temp=0.3).invoke(
        f"Write a polite, concise support reply (max 90 words). Triage: {state['triage']}\nTicket: {state['ticket']}")
    return {
        "draft": msg.content
    }

def needs_review(state: State) -> Literal["review", "send"]:
    t = state["triage"]
    return "review" if t["urgency"] == "high" or t["refund_requested"] or t["sentiment"] == "angry" else "send"

def review_node(state: State) -> Command[Literal["send"]]:
    decision = interrupt({"draft": state["draft"], "triage": state["triage"], "ask": "approve / edit"})
    edited = decision.get("edited_text") if isinstance(decision, dict) else None
    final = edited or state["draft"]
    return Command(goto="send", update={"final": final})

def send_node(state: State) -> dict:
    final = state.get("final") or state["draft"]
    print(f"\n>>> SENT TO CUSTOMER:\n{final}")  # replace with real email/helpdesk API
    return {"final": final, "sent": True}

def build_graph(checkpointer=None):
    b = StateGraph(State)

    b.add_node("triage", triage_node)
    b.add_node("draft", draft_node)
    b.add_node("review", review_node)
    b.add_node("send", send_node)

    b.add_edge(START, "triage")
    b.add_edge("triage", "draft")
    b.add_conditional_edges("draft", needs_review, {"review": "review", "send": "send"})
    b.add_edge("send", END)

    return b.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    g = build_graph(get_checkpointer("memory"))
    tickets = {
        "t-1": "How do I change the email on my account? Thanks!",
        "t-2": "I was charged TWICE and this is unacceptable. I want a refund today!",
    }
    for tid, text in tickets.items():
        cfg = {"configurable": {"thread_id": tid}}
        out = g.invoke({"ticket": text}, cfg)
        if "__interrupt__" in out:
            p = out["__interrupt__"][0].value
            print(f"\n[{tid}] needs human review. triage={p['triage']}\nDRAFT:\n{p['draft']}")
            g.invoke(Command(resume={"edited_text": p["draft"] + "\n\nA manager will follow up personally."}), cfg)

