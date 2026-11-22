from __future__ import annotations

def _fmt(values: dict | None) -> str:
    return "n/a" if not values or not values["total"] else f"{values['passed']}/{values['total']}"

def compare(baseline: dict, changed: dict) -> str:
    base_summary, changed_summary = baseline["summary"], changed["summary"]
    warnings = []
    if baseline["meta"]["cases_sha"] != changed["meta"]["cases_sha"]:
        warnings.append("Datasets differ between runs (cases_sha mismatch); this comparison is not valid.")
    if baseline["meta"]["model_id"] != changed["meta"]["model_id"]:
        warnings.append("Model IDs differ between runs.")
    if changed["meta"].get("model_is_moving_target"):
        warnings.append("Runs used `openrouter/free`, which may route to different models; use a fixed model ID for fair comparison.")
    if changed["meta"].get("top_k") == changed["meta"].get("baseline_top_k"):
        warnings.append("`changed` top_k equals baseline top_k; the variants are identical in this setting.")
    if base_summary["errors"] or changed_summary["errors"]:
        warnings.append(
            f"Errored cases: baseline={base_summary['errors']}, changed={changed_summary['errors']}; "
            "rate limits and crashes are not quality misses."
        )

    lines = ["# Baseline vs changed", ""]
    lines += [
        f"- Baseline: `{baseline['meta']['variant_label']}` ({baseline['meta']['date_utc']}, "
        f"model `{baseline['meta']['model_id']}`, top_k={baseline['meta'].get('top_k')})",
        f"- Changed: `{changed['meta']['variant_label']}` ({changed['meta']['date_utc']}, "
        f"model `{changed['meta']['model_id']}`, top_k={changed['meta'].get('top_k')})", "",
    ]

    lines += [f"> Warning: {warning}" for warning in warnings] + ([""] if warnings else [])
    lines += [
        "| Version | Explicit checks passed | Grounded answers | Route correct | Retrieval hit | Median latency |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for name, summary in (("Baseline", base_summary), ("Changed", changed_summary)):
        lines.append(
            f"| {name} | {summary['explicit_pass']}/{summary['cases']} | "
            f"{_fmt(summary['checks']['grounded'])} | {_fmt(summary['checks']['route_ok'])} | "
            f"{_fmt(summary['checks']['retrieval_hit'])} | {summary['median_latency_s']}s |"
        )

    lines += ["", "## Case-level differences", "", "| Case | Category | Baseline | Changed | Note |", "| --- | --- | --- | --- | --- |"]
    changed_by_id = {row["id"]: row for row in changed["cases"]}
    count = 0

    for before in baseline["cases"]:
        after = changed_by_id.get(before["id"])
        if after is None:
            continue
        before_status = "ERR" if before["error"] else "PASS" if before["passed"] else "FAIL"
        after_status = "ERR" if after["error"] else "PASS" if after["passed"] else "FAIL"
        if before_status != after_status:
            count += 1
            note = "FIXED" if after_status == "PASS" else "REGRESSION" if before_status == "PASS" else "changed"
            lines.append(f"| {before['id']} | {before['category']} | {before_status} | {after_status} | {note} |")
    if not count:
        lines.append("| - | - | - | - | no case changed status |")
    lines += [
        "", "## Security probes (LLM-facing)", "",
        f"- Baseline: {base_summary['security_llm']}",
        f"- Changed: {changed_summary['security_llm']}", "",
    ]
    return "\n".join(lines)