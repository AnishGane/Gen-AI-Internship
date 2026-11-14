"""PROJECT 4 - Parallel code-review assistant (fan-out reviewers -> aggregate -> prioritised report).

uv run .\Week8\projects\p4_code_review_assistant.py .\Week8\core\llm.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from Week10.core.llm import get_llm

class Finding(BaseModel):
    line_hint: str
    severity: Literal["low", "medium", "high"]
    issue: str
    fix: str

class Findings(BaseModel):
    findings: list[Finding]

class State(TypedDict, total=False):
    code: str
    findings: Annotated[list[dict], operator.add]
    report: str

FOCUS = {
    "security": "security problems (injection, secrets, unsafe eval/deserialization, missing validation)",
    "performance": "performance problems (needless loops, repeated I/O, bad data structures)",
    "style": "readability, naming, typing, docstrings, error handling",
}

def make_reviewer(name: str, focus: str):
    def reviewer(s: State) -> dict:
        structured_llm = get_llm().with_structured_output(
            Findings,
            method="function_calling"
        )

        out = structured_llm.invoke(
            f"""
            You are a {name} code reviewer.

            Focus only on: {focus}

            Review the following code carefully.

            Return:
            - Only genuine issues.
            - Accurate line hints.
            - Severity: low, medium, or high.
            - A clear explanation and practical fix.
            - An empty findings list if no issues exist.

            Code:
            {s['code']}
            """
        )

        if out is None:
            raise ValueError(
                f"{name} reviewer returned None instead of Findings."
            )

        if not isinstance(out, Findings):
            raise TypeError(
                f"{name} reviewer returned unexpected type: {type(out)}"
            )

        return {
            "findings": [
                {**finding.model_dump(), "area": name}
                for finding in out.findings
            ]
        }

    return reviewer

def aggregate(s: State) -> dict:
    order = {"high": 0, "medium": 1, "low": 2}
    items = sorted(s["findings"], key=lambda f: order[f["severity"]])
    if not items:
        return {"report": "No issues found."}
    lines = [f"[{f['severity'].upper()}] ({f['area']}) {f['line_hint']}: {f['issue']}\n    fix: {f['fix']}" for f in items]
    return {"report": "\n".join(lines)}

def build_graph():
    b = StateGraph(State)
    for name, focus in FOCUS.items():
        b.add_node(name, make_reviewer(name, focus))
        b.add_edge(START, name)
    b.add_node("aggregate", aggregate)
    b.add_edge(
        ["security", "performance", "style"],
        "aggregate"
    )
    b.add_edge("aggregate", END)
    return b.compile()

if __name__ == "__main__":
    if len(sys.argv) != 2:
      sys.exit("Usage: p4_code_review_assistant.py <file>")
      
    code = Path(sys.argv[1]).read_text(encoding="utf-8")
    print(build_graph().invoke({"code": code, "findings": []})["report"])
