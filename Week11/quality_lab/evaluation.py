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
            runner, retries, question = probes["question"], inject_chunk=probe.get("inject_chunk"), case_id=probe["id"]
        )
        verdict = check_probe(probe, result)
        rows.append({
            "id": probe["id"], "attack": probe["attack"], "question": probe["question"][:200], **verdict,
            "status": result.get("status"), "answer": redact(result.get("answer", ""))[:600],
            "error": result.get("error"), "node_path": result.get("node_path"), "run_id": result.get("run_id"),
        })
        log(f"  {probe['id']:9s} {verdict['outcome'].upper():6s} {probe['attack']}")
    return rows