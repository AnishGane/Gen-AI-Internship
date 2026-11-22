from __future__ import annotations
import argparse
import json
import os
import sys

from Week11.quality_lab.config import CASES_PATH, PROBES_PATH, RESULTS_DIR, VARIANTS
from Week11.quality_lab.data import load_jsonl, validate_cases
from Week11.quality_lab.evaluation import build_meta, run_eval_cases, run_probes, save, summarize
from Week11.quality_lab.reporting import compare
from Week11.quality_lab.runner import make_mock_runner, make_runner
from Week11.quality_lab.security import security_code_checks

def cmd_run(args: argparse.Namespace) -> int:
    if args.no_trace:
        os.environ["LANGSMITH_TRACING"] = "false"
    cases, probes = load_jsonl(CASES_PATH), load_jsonl(PROBES_PATH)
    validate_cases(cases)
    if args.only:
        cases = [case for case in cases if case["id"] in args.only]
    if args.limit:
        cases = cases[:args.limit]
    if args.mock:
        runner, info = make_mock_runner(), {}
    else:
        runner, info = make_runner(args.variant)

    meta = build_meta(args.variant, info, args.mock, CASES_PATH, PROBES_PATH)
    print(f"Variant={args.variant} model={meta['model_id']} sha={meta['git_sha']} mock={args.mock}")
    print("Evaluation cases:")
    rows = run_eval_cases(runner, cases, retries=args.retries, judge=args.judge)

    probe_rows, code_rows = [], []
    if not args.skip_security:
        print("Security probes (model-facing):")
        probe_rows = run_probes(runner, probes, retries=args.retries)
        print("Security checks (code-level):")
        code_rows = security_code_checks()
        for check in code_rows:
            print(f"  {check['id']:9s} {check['outcome'].upper():7s} {check['attack']} - {check['detail']}")

    run = {
        "meta": meta, "summary": summarize(rows, probe_rows, code_rows), "cases": rows,
        "security": probe_rows, "security_code": code_rows,
    }

    path = save(run, args.mock)
    summary = run["summary"]
    print(
        f"\nExplicit checks passed: {summary['explicit_pass']}/{summary['cases']} "
        f"(errors: {summary['errors']}); median latency {summary['median_latency_s']}s; "
        f"security(LLM) {summary['security_llm']}; security(code) {summary['security_code']}"
    )
    print(f"Saved {path}")
    return 0

def cmd_compare(_: argparse.Namespace) -> int:
    baseline_path = RESULTS_DIR / "latest_baseline.json"
    changed_path = RESULTS_DIR / "latest_changed.json"
    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        changed = json.loads(changed_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        print(f"Missing {exc.filename}. Run both variants first (real runs, not --mock).")
        return 1
    markdown = compare(baseline, changed)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "comparison.md").write_text(markdown, encoding="utf-8")
    print(markdown)
    return 0

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate the Week 10 agentic RAG app and probe its defenses.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="run evaluation cases and security probes")
    run_parser.add_argument("--variant", choices=VARIANTS, default="baseline")
    run_parser.add_argument("--judge", action="store_true", help="add a separate LLM faithfulness judgment")
    run_parser.add_argument("--mock", action="store_true", help="offline harness smoke run; not app-quality evidence")
    run_parser.add_argument("--skip-security", action="store_true")
    run_parser.add_argument("--no-trace", action="store_true", help="disable LangSmith tracing for this run")
    run_parser.add_argument("--only", nargs="*", help="run only these evaluation case IDs")
    run_parser.add_argument("--limit", type=int, help="run only the first N evaluation cases")
    run_parser.add_argument("--retries", type=int, default=int(os.getenv("EVAL_RETRIES", "2")))
    run_parser.set_defaults(func=cmd_run)

    compare_parser = subparsers.add_parser("compare", help="compare latest real baseline and changed runs")
    compare_parser.set_defaults(func=cmd_compare)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())