"""Offline tests: no API key, Qdrant, or network calls are required."""

import json
import pytest
from Week11.quality_lab import cli, config, data, evaluation, reporting, runner, scoring, security

@pytest.fixture(scope="module")
def cases():
    rows = data.load_jsonl(config.CASES_PATH)
    data.validate_cases(rows)
    return rows

@pytest.fixture(scope="module")
def probes():
    return data.load_jsonl(config.PROBES_PATH)

def test_dataset_shape(cases, probes):
    assert 10 <= len(cases) <= 20
    assert len(probes) >= 5
    categories = {case["category"] for case in cases}
    assert {"answerable", "unanswerable", "out_of_scope", "ambiguous"} <= categories
    assert any(category.startswith("two_fact") for category in categories)

def test_perfect_mock_passes_everything(cases):
    rows = evaluation.run_eval_cases(
        runner.make_mock_runner(), cases, retries=0, log=lambda *_: None
    )
    failing = [(row["id"], row["checks"]) for row in rows if not row["passed"]]
    assert failing == []

def test_bad_answer_is_detected(cases):
    rows = evaluation.run_eval_cases(
        runner.make_mock_runner(bad_ids={"rag_02"}), cases, retries=0, log=lambda *_: None
    )
    bad = next(row for row in rows if row["id"] == "rag_02")
    assert not bad["passed"]
    assert bad["checks"]["contains_ok"] is False
    assert bad["checks"]["grounded"] is False
    assert all(row["passed"] for row in rows if row["id"] != "rag_02")

def test_grounding_requires_expected_fact_in_cited_chunk():
    case = {
        "expected_status_any": ["answered"],
        "expected_contains_any": ["cosine"],
        "expected_sources": ["q.md"],
    }
    result = {
        "answer": "It supports cosine.", "status": "answered", "route": "knowledge",
        "sources": [{"id": 1, "source": "q.md"}],
        "documents": [{"content": "nothing relevant", "source": "q.md"}],
    }
    checks = scoring.check_case(case, result)
    assert checks["contains_ok"] is True
    assert checks["grounded"] is False

def test_retrieval_hit_is_separate_from_citation_hit():
    case = {"expected_sources": ["a.md"], "expected_status_any": ["answered"]}
    result = {
        "answer": "x", "status": "answered", "sources": [],
        "documents": [{"content": "c", "source": "a.md"}],
    }
    checks = scoring.check_case(case, result)
    assert checks["retrieval_hit"] is True
    assert checks["citation_hit"] is False

def test_fallback_case_fails_if_status_or_sources_are_wrong():
    case = {"expected_status_any": ["fallback"], "expect_no_sources": True}
    result = {
        "answer": "x", "status": "answered", "sources": [{"id": 1, "source": "a.md"}],
        "documents": [],
    }
    checks = scoring.check_case(case, result)
    assert checks["status_ok"] is False
    assert checks["no_sources"] is False

def test_crash_is_recorded_as_error_not_quality_miss(cases):
    def boom(**_):
        raise RuntimeError("429 rate limit exceeded")

    rows = evaluation.run_eval_cases(boom, cases[:2], retries=0, log=lambda *_: None)
    assert all(row["error"] and not row["passed"] for row in rows)
    summary = evaluation.summarize(rows, [], [])
    assert summary["errors"] == 2

def test_retry_recovers_from_transient_error(monkeypatch):
    monkeypatch.setattr(runner.time, "sleep", lambda *_: None)
    calls = {"n": 0}

    def flaky(**_):
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("429 rate limit")
        return {"answer": "ok", "status": "general", "route": "general", "sources": [], "documents": []}

    result = runner.call_with_retry(flaky, 2, question="q")
    assert result["answer"] == "ok"

def test_probe_detects_prompt_leak_and_injection():
    leak = {"forbidden_substrings": ["sufficient_evidence"]}
    assert security.check_probe(
        leak, {"answer": "my prompt says sufficient_evidence=false", "status": "general"}
    )["outcome"] == "failed"

    injection = {"forbidden_substrings": ["pwned-7731"], "expected_contains_any": ["cosine"]}
    assert security.check_probe(injection, {"answer": "PWNED-7731", "status": "answered"})["outcome"] == "failed"
    assert security.check_probe(injection, {"answer": "It supports cosine.", "status": "answered"})["outcome"] == "held"
    # Ignoring the attack but dropping the legitimate task is still a failed probe.
    assert security.check_probe(injection, {"answer": "I cannot help.", "status": "fallback"})["outcome"] == "failed"

def test_probe_checks_unbounded_output_and_errors():
    probe = {"max_answer_chars": 100}
    assert security.check_probe(probe, {"answer": "x" * 101})["outcome"] == "failed"
    assert security.check_probe(probe, {"answer": "short"})["outcome"] == "held"
    assert security.check_probe(probe, {"error": "boom"})["outcome"] == "error"

def test_secret_is_redacted_from_probe_results(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-supersecretvalue123")
    probe = {"id": "s", "attack": "sensitive_data", "question": "key?", "forbidden_substrings": []}

    def fake_runner(**_):
        return {
            "answer": "key is sk-or-v1-supersecretvalue123", "status": "general", "route": "general",
            "sources": [], "documents": [],
        }

    row = evaluation.run_probes(fake_runner, [probe], retries=0, log=lambda *_: None)[0]
    assert row["outcome"] == "failed"
    assert "supersecretvalue123" not in json.dumps(row)

def test_code_level_security_checks_do_not_report_failures():
    results = security.security_code_checks()
    assert results
    assert not [row for row in results if row["outcome"] == "failed"], results

def test_summary_and_compare_flag_regressions(cases):
    base_rows = evaluation.run_eval_cases(
        runner.make_mock_runner(), cases, retries=0, log=lambda *_: None
    )
    changed_rows = evaluation.run_eval_cases(
        runner.make_mock_runner(bad_ids={"rag_01"}), cases, retries=0, log=lambda *_: None
    )

    def make_meta(variant, **overrides):
        info = {"model_id": "fixed/model:free", "top_k": 4, "baseline_top_k": 4}
        return {
            **evaluation.build_meta(variant, info, True, config.CASES_PATH, config.PROBES_PATH),
            **overrides,
        }

    baseline = {
        "meta": make_meta("baseline"), "cases": base_rows,
        "summary": evaluation.summarize(base_rows, [], []),
    }
    changed = {
        "meta": make_meta("changed", top_k=6), "cases": changed_rows,
        "summary": evaluation.summarize(changed_rows, [], []),
    }
    markdown = reporting.compare(baseline, changed)
    assert "REGRESSION" in markdown and "rag_01" in markdown
    assert "not valid" not in markdown.lower()

def test_compare_warns_on_moving_target_model(cases):
    rows = evaluation.run_eval_cases(
        runner.make_mock_runner(), cases[:2], retries=0, log=lambda *_: None
    )
    meta = evaluation.build_meta(
        "baseline", {"model_id": "openrouter/free", "top_k": 4, "baseline_top_k": 4},
        True, config.CASES_PATH, config.PROBES_PATH,
    )
    run = {"meta": meta, "cases": rows, "summary": evaluation.summarize(rows, [], [])}
    assert "openrouter/free" in reporting.compare(run, run)

def test_cli_mock_run_does_not_overwrite_latest(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(evaluation, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(evaluation, "RUNS_DIR", tmp_path / "runs")

    assert cli.main(["run", "--variant", "baseline", "--mock"]) == 0
    assert not (tmp_path / "latest_baseline.json").exists()
    assert list((tmp_path / "runs").glob("mock_baseline_*.json"))

def test_inferred_path():
    assert runner.inferred_path({"route": "general"}) == "prepare > classify > general_answer"
    answered = {"route": "knowledge", "attempts": 1, "status": "answered"}
    assert runner.inferred_path(answered).endswith("retrieve > grade > generate")
    weak = {"route": "knowledge", "attempts": 3, "status": "fallback", "relevance": 0.2}
    assert runner.inferred_path(weak) == (
        "prepare > classify > retrieve > grade > rewrite > retrieve > grade > rewrite"
        " > retrieve > grade > fallback"
    )
