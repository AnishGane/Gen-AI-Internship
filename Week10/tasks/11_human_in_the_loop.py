"""Day 4 / Task 2 - plan -> human approval (interrupt) -> execute | revise.

A checkpointer is REQUIRED: interrupt() saves state, and Command(resume=...) continues the same thread.
Set CHECKPOINTER=sqlite to resume even after the process restarts.
"""
import operator
import uuid
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from Week10.core.llm import get_llm
from Week10.lg.memory import get_checkpointer

MAX_REVISIONS = 3

class State(TypedDict, total=False):
    request: str
    plan: str
    feedback: str
    revisions: int
    status: str
    audit: Annotated[list[str], operator.add]

def plan_node(state: State) -> dict:
    msg = get_llm().invoke(
        f"Write a short numbered plan (max 4 steps) for this operation. Do not execute anything.\n{state['request']}")
    return {"plan": msg.content, "revisions": 0, "audit": ["plan created"]}

def approval_node(state: State) -> Command[Literal["execute", "revise", "cancel"]]:
    if state.get("revisions", 0) >= MAX_REVISIONS:
        return Command(goto="cancel")
    # Execution pauses HERE. The payload is returned to the caller; the resume value comes back from interrupt().
    decision = interrupt({"question": "Approve this plan?", "plan": state["plan"]})
    if decision.get("approved"):
        return Command(goto="execute", update={"audit": ["approved by human"]})
    return Command(goto="revise", update={"feedback": decision.get("feedback", ""), "audit": ["rejected by human"]})

def revise_node(state: State) -> dict:
    msg = get_llm().invoke(
        f"Revise this plan using the reviewer feedback. Keep it to max 4 numbered steps.\n"
        f"Plan:\n{state['plan']}\nFeedback: {state['feedback']}")
    return {"plan": msg.content, "revisions": state.get("revisions", 0) + 1, "audit": ["plan revised"]}

def execute_node(state: State) -> dict:
    print("   >>> EXECUTING approved plan (simulated)")  # the sensitive action happens ONLY after approval
    return {"status": "executed", "audit": ["executed"]}

def cancel_node(state: State) -> dict:
    return {"status": "cancelled", "audit": ["cancelled: too many revisions"]}

def build_graph(checkpointer):
    b = StateGraph(State)
    b.add_node("plan", plan_node)
    b.add_node("approval", approval_node)
    b.add_node("revise", revise_node)
    b.add_node("execute", execute_node)
    b.add_node("cancel", cancel_node)
    b.add_edge(START, "plan")
    b.add_edge("plan", "approval")
    b.add_edge("revise", "approval")
    b.add_edge("execute", END)
    b.add_edge("cancel", END)
    return b.compile(checkpointer=checkpointer)

def show_interrupt(result: dict) -> bool:
    if "__interrupt__" in result:
        payload = result["__interrupt__"][0].value
        print(f"\n--- PAUSED: {payload['question']}\n{payload['plan']}\n")
        return True
    return False

def main():
    graph = build_graph(get_checkpointer())
    cfg = {"configurable": {"thread_id": f"ops-{uuid.uuid4().hex[:8]}"}}

    result = graph.invoke({"request": "Archive all customer records older than 5 years", "audit": []}, cfg)
    show_interrupt(result)

    # Human rejects with feedback -> graph revises and pauses again
    result = graph.invoke(Command(resume={"approved": False, "feedback": "Add a backup step first."}), cfg)
    show_interrupt(result)

    # Human approves -> graph executes
    result = graph.invoke(Command(resume={"approved": True}), cfg)
    print("final status:", result["status"])
    print("audit trail :", result["audit"])

if __name__ == "__main__":
    main()
