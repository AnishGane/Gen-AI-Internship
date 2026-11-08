"""Agentic RAG workflow (LangGraph).

START -> prepare -> classify -+-> general_answer -> END
                              +-> retrieve -> [grade -> (good) generate | (weak) rewrite -> retrieve | (exhausted) fallback]
                                              generate -> END | fallback (insufficient evidence)
"""

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from Week8.config import settings
from Week8.core.llm import get_llm
from Week8.core.prompts import GENERAL_SYSTEM, RAG_ROUTE_PROMPT
from Week8.logger import get_logger
from Week8.models import RagRoute
from Week8.RAG.answer_generator import build_sources, generate_grounded_answer
from Week8.RAG.evaluator import grade_documents
from Week8.RAG.query_rewriter import rewrite_query
from Week8.RAG.retriever import retrieve_chunks

log = get_logger("rag.workflow")

FALLBACK_MESSAGE = (
    "I couldn't find enough reliable information in the knowledge base to answer that. "
    "Try rephrasing the question or adding more detail."
)

class RAGState(TypedDict, total=False):
    question: str
    messages: Annotated[list[AnyMessage], add_messages]  # conversation history (persisted per thread)
    route: str
    query: str              # current search query (may be rewritten)
    documents: list[dict]
    relevance: float
    grade_reason: str
    attempts: int           # number of retrieval attempts so far
    rewrites: list[str]
    answer: str
    sources: list[dict]
    status: str             # general | answered | fallback

# ---------------- helper seams (monkeypatched in tests) ----------------
def classify_query(question: str) -> str:
    llm = get_llm().with_structured_output(RagRoute, method="function_calling")
    return llm.invoke(RAG_ROUTE_PROMPT.format_messages(question=question)).route

# ---------------- nodes ----------------
def prepare(state: RAGState) -> dict:
    """Reset per-turn fields (checkpointed state survives between turns of the same thread)."""
    q = state["question"]
    return {"query": q, "documents": [], "relevance": 0.0, "grade_reason": "", "attempts": 0, "rewrites": [],
            "answer": "", "sources": [], "status": "", "messages": [HumanMessage(q)]}

def classify(state: RAGState) -> dict:
    route = classify_query(state["question"])
    log.info("route=%s", route)
    return {"route": route}

def general_answer(state: RAGState) -> dict:
    reply = get_llm(temp=0.5).invoke([SystemMessage(GENERAL_SYSTEM), *state["messages"]])
    return {"answer": reply.content, "status": "general", "messages": [AIMessage(reply.content)]}

def retrieve(state: RAGState) -> dict:
    docs = retrieve_chunks(state["query"])
    log.info("retrieve attempt=%d query=%r hits=%d", state.get("attempts", 0) + 1, state["query"], len(docs))
    return {"documents": docs, "attempts": state.get("attempts", 0) + 1}

def grade(state: RAGState) -> dict:
    g = grade_documents(state["question"], state["documents"])
    log.info("relevance=%.2f", g.score)
    return {"relevance": g.score, "grade_reason": g.reason}

def rewrite(state: RAGState) -> dict:
    new_query = rewrite_query(state["question"], state["query"], state.get("grade_reason", ""))
    log.info("rewrite -> %r", new_query)
    return {"query": new_query, "rewrites": [*state.get("rewrites", []), new_query]}

def generate(state: RAGState) -> dict:
    result = generate_grounded_answer(state["question"], state["documents"])
    sources = build_sources(state["documents"], result.citations)
    if not result.sufficient_evidence or not sources:
        return {"status": "insufficient"}  # routed to fallback
    return {"answer": result.answer, "sources": sources, "status": "answered",
            "messages": [AIMessage(result.answer)]}

def fallback(state: RAGState) -> dict:
    return {"answer": FALLBACK_MESSAGE, "sources": [], "status": "fallback",
            "messages": [AIMessage(FALLBACK_MESSAGE)]}

# ---------------- routing ----------------
def route_after_classify(state: RAGState) -> Literal["general_answer", "retrieve"]:
    return "general_answer" if state["route"] == "general" else "retrieve"

def route_after_grade(state: RAGState) -> Literal["generate", "rewrite", "fallback"]:
    if state.get("relevance", 0.0) >= settings.relevance_threshold:
        return "generate"
    if state.get("attempts", 0) < 1 + settings.max_retries:  # BOUNDED: first try + MAX_RETRIES retries
        return "rewrite"
    return "fallback"

def route_after_generate(state: RAGState) -> Literal["fallback", "__end__"]:
    return "fallback" if state.get("status") == "insufficient" else END

# ---------------- graph ----------------
def build_rag_graph(checkpointer=None, adaptive: bool = True):
    b = StateGraph(RAGState)
    for name, fn in [("prepare", prepare), ("classify", classify), ("general_answer", general_answer),
                     ("retrieve", retrieve), ("generate", generate), ("fallback", fallback)]:
        b.add_node(name, fn)
    b.add_edge(START, "prepare")
    b.add_edge("prepare", "classify")
    b.add_conditional_edges("classify", route_after_classify)
    b.add_edge("general_answer", END)

    if adaptive:
        b.add_node("grade", grade)
        b.add_node("rewrite", rewrite)
        b.add_edge("retrieve", "grade")
        b.add_conditional_edges("grade", route_after_grade)
        b.add_edge("rewrite", "retrieve")
    else:
        b.add_edge("retrieve", "generate")

    b.add_conditional_edges("generate", route_after_generate)
    b.add_edge("fallback", END)
    return b.compile(checkpointer=checkpointer)

# ---------------- convenience ----------------
def ask(graph, question: str, thread_id: str, extra_config: dict | None = None) -> dict:
    cfg = {"configurable": {"thread_id": thread_id}, "run_name": "agentic_rag", "tags": ["week8"],
           "metadata": {"thread_id": thread_id}, **(extra_config or {})}
    return graph.invoke({"question": question}, cfg)

def summarize(state: dict) -> dict:
    return {"answer": state.get("answer", ""), "status": state.get("status", ""), "route": state.get("route", ""),
            "sources": state.get("sources", []), "attempts": state.get("attempts", 0),
            "rewrites": state.get("rewrites", []), "relevance": state.get("relevance", 0.0)}
