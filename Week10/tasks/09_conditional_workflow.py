"""Day 3 / Task 3 - classify -> route (general | math | technical) -> generate, with a BOUNDED retry loop.
"""
import sys
from typing import Literal, TypedDict

from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, START, StateGraph

from Week10.core.llm import get_llm
from Week10.core.prompts import ANSWER_PROMPT_SIMPLE, MATH_PROMPT, ROUTE_PROMPT
from Week10.core.tools import safe_eval, search_text
from Week10.models import MathExpression, QueryRoute

MAX_CALC_ATTEMPTS = 2

class State(TypedDict, total=False):
    query: str
    route: str
    expression: str
    context: str       # tool result / retrieved text
    error: str
    attempts: int
    answer: str

# ---------------- nodes ----------------
def classify(state: State) -> dict:
    decision = get_llm().with_structured_output(QueryRoute, method="function_calling").invoke(
        ROUTE_PROMPT.format_messages(query=state["query"]))
    return {"route": decision.route, "attempts": 0}

def extract_expression(state: State) -> dict:
    hint = f"Your previous expression failed with: {state['error']}. Fix it." if state.get("error") else ""
    out = get_llm().with_structured_output(MathExpression, method="function_calling").invoke(
        MATH_PROMPT.format_messages(query=state["query"], hint=hint))
    return {"expression": out.expression}

def calculator_node(state: State) -> dict:
    try:
        return {"context": f"{state['expression']} = {safe_eval(state['expression'])}", "error": ""}
    except Exception as exc:
        return {"error": str(exc), "attempts": state.get("attempts", 0) + 1}

def knowledge_search(state: State) -> dict:
    return {"context": search_text.invoke({"query": state["query"]})}

def generate(state: State) -> dict:
    context = state.get("context") or "(none - answer from general knowledge)"
    chain = ANSWER_PROMPT_SIMPLE | get_llm(temperature=0.2) | StrOutputParser()
    return {"answer": chain.invoke({"query": state["query"], "context": context})}

# ---------------- routing ----------------
def route_query(state: State) -> Literal["generate", "extract_expression", "knowledge_search"]:
    return {"general": "generate", "math": "extract_expression", "technical": "knowledge_search"}.get(
        state.get("route"), "generate"
    )

def after_calculator(state: State) -> Literal["extract_expression", "generate"]:
    if state.get("error") and state.get("attempts", 0) < MAX_CALC_ATTEMPTS:
        return "extract_expression"  # loop back (bounded!)
    return "generate"                # success OR gave up -> answer anyway

def build_graph():
    b = StateGraph(State)
    b.add_node("classify", classify)
    b.add_node("extract_expression", extract_expression)
    b.add_node("calculator", calculator_node)
    b.add_node("knowledge_search", knowledge_search)
    b.add_node("generate", generate)
    b.add_edge(START, "classify")
    b.add_conditional_edges("classify", route_query)
    b.add_edge("extract_expression", "calculator")
    b.add_conditional_edges("calculator", after_calculator)
    b.add_edge("knowledge_search", "generate")
    b.add_edge("generate", END)
    return b.compile()

# ---------------- offline bounded-loop demo ----------------
class RetryState(TypedDict):
    attempts: int
    ok: bool

def build_retry_demo(succeed_on: int, max_attempts: int = 3):
    def try_op(s: RetryState) -> dict:
        n = s["attempts"] + 1
        print(f"  attempt {n}")
        return {"attempts": n, "ok": n >= succeed_on}

    def decide(s: RetryState) -> Literal["try_op", "__end__"]:
        return END if s["ok"] or s["attempts"] >= max_attempts else "try_op"

    b = StateGraph(RetryState)
    b.add_node("try_op", try_op)
    b.add_edge(START, "try_op")
    b.add_conditional_edges("try_op", decide)
    return b.compile()

if __name__ == "__main__":
    if "--retry" in sys.argv:
        print("succeeds on 2nd try:", build_retry_demo(2).invoke({"attempts": 0, "ok": False}))
        print("never succeeds (stops at 3):", build_retry_demo(99).invoke({"attempts": 0, "ok": False}))
    else:
        graph = build_graph()
        for q in ["Hi, can you write a haiku about rain?", "What is (125 * 4) + 18% of 200?",
                  "How do reducers work in LangGraph state?"]:
            out = graph.invoke({"query": q})
            print(f"\nQ: {q}\n route={out['route']}\n A: {out['answer']}")
