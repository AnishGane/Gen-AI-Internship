from __future__ import annotations
import re
from pathlib import Path

def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower())

def _contains(text: str, case: dict) -> bool | None:
    normalized = _norm(text)
    any_terms = case.get("expected_contains_any")
    all_terms = case.get("expected_contains_all")
    if not any_terms and not all_terms:
        return None
    ok = True
    if any_terms:
        ok &= any(_norm(term) in normalized for term in any_terms)
    if all_terms:
        ok &= all(_norm(term) in normalized for term in all_terms)
    return ok

def _source_names(items: list[dict]) -> set[str]:
    return {Path(str(item.get("source", ""))).name for item in items}

def check_case(case: dict, result: dict) -> dict[str, bool | None]:
    """Run deterministic checks. None means the check does not apply to this case."""
    checks: dict[str, bool | None] = {"no_error": not result.get("error")}
    if result.get("error"):
        return checks

    sources = result.get("sources", [])
    documents = result.get("documents", [])
    if "expected_route" in case:
        checks["route_ok"] = result.get("route") == case["expected_route"]
    if "expected_status_any" in case:
        checks["status_ok"] = result.get("status") in case["expected_status_any"]
    checks["contains_ok"] = _contains(result.get("answer", ""), case)

    wanted = [Path(source).name for source in case.get("expected_sources", [])]
    if wanted:
        checks["retrieval_hit"] = set(wanted) <= _source_names(documents)
        checks["citation_hit"] = set(wanted) <= _source_names(sources)
    if case.get("expect_no_sources"):
        checks["no_sources"] = not sources

    if result.get("status") == "answered" and (
        case.get("expected_contains_any") or case.get("expected_contains_all")
    ):
        cited_text = " ".join(
            documents[source["id"] - 1]["content"]
            for source in sources
            if 1 <= source.get("id", 0) <= len(documents)
        )
        checks["grounded"] = bool(sources) and bool(_contains(cited_text, case))
    elif case.get("expected_status_any") == ["answered"]:
        checks["grounded"] = False
    return checks

def case_passed(checks: dict) -> bool:
    return all(value for value in checks.values() if value is not None)