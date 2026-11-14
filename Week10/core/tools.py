"""Custom tools: calculator, date/time, local text search."""

import ast
import operator
import re
from datetime import datetime, timezone
from pathlib import Path
from langchain_core.tools import tool

KB_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_docs"

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.Mod: operator.mod, ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}

def safe_eval(expression: str) -> float:
    """Evaluate arithmetic WITHOUT eval(): walk the AST and allow only numbers and basic operators."""

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            left, right = _eval(node.left), _eval(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100 or abs(left) > 10**6:
                raise ValueError("operands too large")
            return _OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.operand))
        raise ValueError("unsupported expression")

    return _eval(ast.parse(expression.strip(), mode="eval"))

@tool
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression such as '(12 + 8) * 3' or '2 ** 10'. Use for ANY maths."""
    try:
        return str(safe_eval(expression))
    except ZeroDivisionError:
        return "Error: division by zero"
    except Exception as exc:  # return errors as text so the model can recover
        return f"Error: {exc}"

@tool
def get_current_datetime() -> str:
    """Return the current date and time in UTC (ISO format). Use when the user asks about today's date or time."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def _paragraphs() -> list[tuple[str, str]]:
    out = []
    for path in sorted(KB_DIR.glob("*.md")):
        for para in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
            if para.strip():
                out.append((path.name, para.strip()))
    return out

@tool
def search_text(query: str) -> str:
    """Keyword search over the local sample documents (LangChain, LangGraph, RAG, Qdrant notes).
    Use for knowledge questions about those topics."""
    terms = {t for t in re.findall(r"\w+", query.lower()) if len(t) > 2}
    scored = []
    for name, para in _paragraphs():
        words = set(re.findall(r"\w+", para.lower()))
        score = len(terms & words)
        if score:
            scored.append((score, name, para))
    scored.sort(reverse=True)
    if not scored:
        return "No matching text found."
    return "\n\n".join(f"[{name}] {para}" for _, name, para in scored[:3])