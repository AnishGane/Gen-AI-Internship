from __future__ import annotations
import json
import statistics
from datetime import datetime, timezone

from Week11.quality_lab.config import RESULTS_DIR, RUNS_DIR, VARIANTS
from Week11.quality_lab.data import file_sha, redact
from Week11.quality_lab.judge import judge_faithfulness
from Week11.quality_lab.runner import git_sha
from Week11.quality_lab.scoring import case_passed, check_case, _source_names
from Week11.quality_lab.security import check_probe

def run_eval_cases(runner, cases: list[str], retries: int = 2, judge: bool = False, log=print) -> list[dict]:
    from Week11.quality_lab.runner import call_with_retry

    rows = []
    for case in cases:
        result = call_with_retry(runner, retries,question=case["question"], case_id=case["id"])
        checks = check_case(case, result)
        row = {
            "id": case["id"], "category": case.get("category"), "subjective": bool(case.get("subjective")),
            "question": case["question"], "checks": checks, "passed": case_passed(checks),
            "error": result.get("error"), "status": result.get("status"), "route": result.get("route"),
            "answer": redact(result.get("answer", "")), "cited": sorted(_source_names(result.get("sources", []))),
            "retrieved": sorted(_source_names(result.get("documents", []))), "attempts": result.get("attempts"),
            "rewrites": result.get("rewrites"), "relevance": result.get("relevance"),
            "latency_s": round(result.get("latency_s", 0.0), 3), "node_path": result.get("node_path"),
            "run_id": result.get("run_id"),
        }
        if judge and result.get("status") == "answered":
            documents = result.get("documents", [])
            row["judge_faithful"] = judge_faithfulness(
                result["answer"], [
                    documents[source["id"] - 1]["content"]
                    for source in result.get("sources", [])
                    if 1 <= source.get("id", 0) <= len(documents)
                ],
            )
        failed = [name for name, value in checks.items() if value is False]
        label = "PASS" if row["passed"] else ("ERROR" if result.get("error") else "FAIL")
        log(f"  {case['id']:9s} {label:5s} {result.get('status', '?'):9s} {row['latency_s']:6.1f}s  {','.join(failed)}")
        rows.append(row)
    return rows

def run_probes(runner, probes:list[dict], retries: int = 2, log=print) -> list[dict]:
    from Week11.quality_lab.runner import call_with_retry

    rows = []
    for probe in probes:
        result = call_with_retry(
            runner, retries, question = probe["question"], inject_chunk=probe.get("inject_chunk"), case_id=probe["id"]
        )
        verdict = check_probe(probe, result)
        rows.append({
            "id": probe["id"], "attack": probe["attack"], "question": probe["question"][:200], **verdict,
            "status": result.get("status"), "answer": redact(result.get("answer", ""))[:600],
            "error": result.get("error"), "node_path": result.get("node_path"), "run_id": result.get("run_id"),
        })
        log(f"  {probe['id']:9s} {verdict['outcome'].upper():6s} {probe['attack']}")
    return rows

def summarize(rows: list[dict], probes: list[dict], code_checks: list[dict]) -> dict:
    def rate(check: str) -> dict:
        values = [row["checks"][check] for row in rows if row["checks"].get(check) is not None]
        return {"passed": sum(values), "total": len(values)}

    errors = sum(bool(row["error"]) for row in rows)
    latencies = [row["latency_s"] for row in rows if not row["error"]]
    judged = [row["judge_faithful"] for row in rows if row.get("judge_faithful") is not None]
    by_category: dict[str, dict] = {}
    for row in rows:
        category = row["category"] or "?"
        group = by_category.setdefault(category, {"passed": 0, "total": 0})
        group["total"] += 1
        group["passed"] += row["passed"]

    return {
        "cases": len(rows), "errors": errors, "explicit_pass": sum(row["passed"] for row in rows),
        "checks": {name: rate(name) for name in (
            "route_ok", "status_ok", "contains_ok", "retrieval_hit", "citation_hit", "no_sources", "grounded"
        )},
        "by_category": by_category,
        "median_latency_s": round(statistics.median(latencies), 2) if latencies else None,
        "judge_faithful": {"passed": sum(judged), "total": len(judged)} if judged else None,
        "security_llm": {outcome: sum(probe["outcome"] == outcome for probe in probes)
                         for outcome in ("held", "failed", "error")},
        "security_code": {outcome: sum(check["outcome"] == outcome for check in code_checks)
                          for outcome in ("held", "failed", "skipped")},
    }

def build_meta(variant: str, info: dict, mock: bool, cases_path, probes_path) -> dict:
    model = info.get("model_id", "mock")
    return {
        "variant": variant, "variant_label": VARIANTS[variant]["label"],
        "date_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "git_sha": git_sha(),
        "app": "Week 10 agentic RAG (LangGraph, adaptive=True)",
        "prompt_version": "Week10/core/prompts.py @ git_sha (unchanged between variants)",
        "model_id": model, "model_is_moving_target": model == "openrouter/free",
        "cases_sha": file_sha(cases_path), "probes_sha": file_sha(probes_path), "mock": mock, **info,
    }

def save(run: dict, mock: bool) -> object:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_path = RUNS_DIR / f"{'mock_' if mock else ''}{run['meta']['variant']}_{stamp}.json"
    raw_path.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    if not mock:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        latest = RESULTS_DIR / f"latest_{run['meta']['variant']}.json"
        latest.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    return raw_path