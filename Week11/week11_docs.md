# Week 11 Quality Lab

A reusable evaluation and security harness for the Week 10 LangGraph agentic RAG application. It imports and evaluates the Week 10 app; it does not implement a second RAG pipeline.

## Project layout

```text
Week11/
├── eval.py                  # command-line entry point
├── quality_lab/
│   ├── config.py            # paths, variants, and shared types
│   ├── data.py              # JSONL loading and secret redaction
│   ├── scoring.py           # deterministic answer checks
│   ├── security.py          # model-facing and code-level probes
│   ├── runner.py            # real Week 10 adapter and offline mock
│   ├── judge.py             # optional LLM-as-judge
│   ├── evaluation.py        # run cases, summarize, and save results
│   ├── reporting.py         # baseline vs changed Markdown report
│   └── cli.py               # command parsing and orchestration
├── data/
│   ├── eval_cases.jsonl
│   └── security_probes.jsonl
└── results/
    └── runs/                # raw run records; ignored by Git
```

The real runner imports `Week10.RAG.workflow`, Week 10 settings, tools, and models. It is designed to run from the repository's existing `uv` environment, where the Week 10 dependencies are installed. If the repository root is somewhere else, set `GENAI_REPO_ROOT` to its absolute path.

## Run the offline harness smoke check

From the repository root, run:

```powershell
cd .\Week11
uv run .\eval.py run --variant baseline --mock
```

The mock runner checks that JSONL loading, scoring, output writing, and report plumbing work. It fabricates answers from expected case data, so **mock results are not evidence of the real model or RAG app's quality**. Mock runs are saved with a `mock_` prefix and are never used by `compare`.

## Run real evaluations

Configure the same OpenRouter, Qdrant, and LangSmith environment variables that Week 10 uses, then run both variants from the repository root:

```powershell
uv run .\eval.py run --variant baseline   
uv run .\eval.py run --variant changed
uv run .\eval.py compare
```

The baseline uses Week 10's configured `top_k`; the changed variant sets `top_k=6`. This is one controlled change. Update `quality_lab/config.py` if you want to test a different hypothesis.

Use `--judge` to add an optional, separate LLM faithfulness score. Deterministic checks remain the primary signal. Use `--no-trace` to disable LangSmith tracing for a run, `--skip-security` to skip probes, `--only rag_01 rag_02` to select cases, or `--limit 3` to limit a run.

## What gets measured

- Route and status behavior.
- Expected answer terms.
- Whether expected documents were retrieved and cited.
- A deterministic grounding proxy: expected facts appear in cited retrieved chunks.
- Expected no-source behavior.
- Median latency and case-level error counts.
- Model-facing security probes and selected Week 10 code-level defense checks.
- An optional LLM-as-judge faithfulness score, stored separately from deterministic checks.

The harness records crashes and rate-limit failures as errors. It does not quietly count them as quality misses. `openrouter/free` may route to a different model over time, so comparison output warns when that moving target was used. For a steadier experiment, use the same fixed free model ID for both variants and record it.

## Results and sensitive data

Real runs save timestamped JSON in `results/runs/` and latest per-variant JSON in `results/`. `compare` writes `results/comparison.md`. The project ignores run JSON by default because responses or traces may contain sensitive information; review any result before sharing or committing it. API keys are redacted from error strings and should only be supplied through environment variables.

## Dataset format

Each non-empty line in `data/eval_cases.jsonl` is one JSON object. Cases can include `id`, `question`, `category`, `expected_route`, `expected_status_any`, `expected_contains_any`, `expected_contains_all`, `expected_sources`, and `expect_no_sources`. Security probe rows in `security_probes.jsonl` can include `attack`, `forbidden_substrings`, `expected_status_any`, `expected_contains_any`, `max_answer_chars`, and `inject_chunk`.

Keep examples representative, avoid private user data, and edit the datasets only when you intentionally want to change the evaluation set. The report records a hash of each dataset so comparisons can detect mismatches.

## Extras

```python
Runner = Callable[..., dict]
```

This creates the type alias `Runner`. It describes a function that can accept any number of `arguments (...)` and returns a `dictionary (dict)`. It’s a hint for readers and type-checking tools; it doesn’t change how the function runs.

```python
SECRET_RE = re.compile(r"(sk-or-[A-Za-z0-9_\-]{10,}|lsv2_[A-Za-z0-9_\-]{10,})")
```

This compiles a regular expression into `SECRET_RE`, so the program can search text for strings that look like `OpenRouter` or `LangSmith API keys`:
- `sk-or- or lsv2_`: the expected key prefix.
- `[A-Za-z0-9_\-]{10,}`: at least 10 letters, numbers, underscores, or hyphens after the prefix.
- `|`: means “or,” so either pattern can match.
- `r"..."`: makes this a raw string, which helps Python pass the backslashes to the regex as written.
The harness uses this pattern to find and redact likely keys before saving error messages or answers. It’s a basic safety net, not a complete secret detector.

`:=` is Python’s assignment expression operator, also called the **walrus operator**. It assigns a value to a variable and lets you use that value in the same expression.