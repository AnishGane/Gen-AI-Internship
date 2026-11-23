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

## `cli.py`

This module is a command-line tool for evaluating the Week 10 agentic RAG application. It can run evaluation cases, run security probes and code-level security checks, save results, and compare the latest baseline and changed runs.

#### Imports

- `annotations` from `__future__` postpones evaluation of type annotations. This helps with forward references and modern type hints.
- `argparse` builds the command-line interface.
- `json`, `os`, and `sys` handle JSON files, environment settings, and the program exit code.
- The `Week11.quality_lab` imports provide the case and probe file paths, result directory, variant names, data loading and validation, evaluation helpers, reporting, model runners, and security checks.

`cmd_run(args)` — run an evaluation

This function handles the `run` subcommand and returns an integer status code.

1. If `--no-trace` was supplied, it sets `LANGSMITH_TRACING=false` in the environment to disable LangSmith tracing for this run.
2. It loads the evaluation cases and security probes from their JSONL files, then validates the cases.
3. It optionally filters cases using `--only` and truncates them using `--limit`.
4. It selects a runner:
   - With `--mock`, it uses a local mock runner. This is intended for an offline harness smoke run, not as evidence of application quality.
   - Otherwise, it creates a real runner for the selected variant.
5. It builds metadata describing the run, including its variant, runner information, whether it is a mock run, and the input paths. It prints a short summary of the variant, model, Git SHA, and mock status.
6. It runs the evaluation cases, passing the selected retry count and whether a separate LLM judge should be used.
7. Unless `--skip-security` was supplied, it runs the model-facing security probes and the code-level security checks. It prints each code check's ID, outcome, attack description, and detail.
8. It assembles the metadata, summarized results, case results, and security results into a single `run` object.
9. It saves that object and prints the explicit-check pass count, error count, median latency, security summaries, and saved file path.
10. It returns `0` to indicate the command completed.

`cmd_compare(args)` — compare two saved runs

This function handles the `compare` subcommand.

- It reads `latest_baseline.json` and `latest_changed.json` from the results directory.
- If either file is missing, it prints an instruction to run both variants as real runs (not mock runs) and returns `1`.
- Otherwise, it compares the two run objects, writes the resulting Markdown report to `comparison.md`, prints the report, and returns `0`.

The comparison therefore depends on both latest-run files already existing.

`main(argv)` — define and dispatch CLI commands

`main` creates the argument parser and defines two required subcommands: `run` and `compare`. The `argv` parameter allows arguments to be supplied directly in code; when it is `None`, `argparse` reads the normal command-line arguments.

#### `run` options

| Option | Meaning |
| --- | --- |
| `--variant` | Selects a variant from `VARIANTS`; defaults to `baseline`. |
| `--judge` | Adds a separate LLM faithfulness judgment. |
| `--mock` | Runs the offline mock harness. Its results are not app-quality evidence. |
| `--skip-security` | Skips both model-facing probes and code-level security checks. |
| `--no-trace` | Disables LangSmith tracing for the run. |
| `--only ID ...` | Runs only cases whose IDs are listed. |
| `--limit N` | Runs only the first `N` cases after filtering. |
| `--retries N` | Sets the retry count. The default comes from `EVAL_RETRIES`, or `2` if that environment variable is unset. |

The `compare` subcommand takes no additional options in this code.

After parsing arguments, `main` calls the handler stored for the selected subcommand (`cmd_run` or `cmd_compare`) and returns its result.

#### Script entry point

```python
if __name__ == "__main__":
    sys.exit(main())
```

This makes the file runnable as a script. `main()` runs the selected command, and `sys.exit` passes its return code back to the operating system.

#### Typical usage

```bash
uv run <script>.py run --variant baseline
uv run <script>.py compare
uv run <script>.py run --variant changed --judge
```

The exact script filename depends on where this code is saved. Run both baseline and changed as real runs before using `compare`, since the comparison command expects their latest result files.

---

## `data.py`

This module provides four small helpers for the Week 11 quality lab: reading JSON Lines files, validating evaluation cases, creating a short file fingerprint, and removing secrets from text before it is saved or shown.

#### Imports

- `hashlib` computes a SHA-256 digest for a file.
- `Path` represents filesystem paths.
- `SECRET_RE` is a regular expression imported from the quality lab configuration. It detects strings that look like secrets or keys.

## `load_jsonl(path)` — read a JSON Lines file

JSONL files contain one JSON value per line. This function reads the file as UTF-8 and processes its lines in order.

- Blank or whitespace-only lines are skipped.
- Each nonblank line is parsed with `json.loads` and appended to the returned list.
- If a line contains invalid JSON, the function raises a `ValueError` that includes the filename, one-based line number, and JSON parser error. The original parsing exception is preserved as the cause.

The return value is a list of dictionaries according to the type hint, although `json.loads` itself can parse other JSON value types too.

#### `validate_cases(cases)` — check required case fields

This function checks a list of evaluation case dictionaries.

1. It collects each case's `id` and checks for duplicates. Duplicate IDs raise `ValueError("duplicate case ids")`.
2. It checks that every case has a truthy `id` and `question`. If either is missing or empty, it raises a `ValueError` that includes the offending case.

If all cases pass, the function returns `None` normally.

#### `file_sha(path)` — create a short file fingerprint

This function reads the file's bytes, calculates a SHA-256 hash, and returns the first 12 hexadecimal characters. The shortened digest can identify or compare file versions in run metadata without printing the full hash.

#### `secrets()` — collect configured API keys

The function checks the environment for three variables:

- `OPENROUTER_API_KEY`
- `QDRANT_API_KEY`
- `LANGSMITH_API_KEY`

It returns the values that are set and nonempty. Variable names without values are omitted.

#### `redact(text)` — remove secret values and key-shaped strings

This function helps prevent credentials from being written to result files:

1. It replaces each configured secret value returned by `secrets()` with `[REDACTED]`.
2. It applies `SECRET_RE` to the remaining text and replaces any matching key-shaped strings with `[REDACTED]` as well.

It returns the cleaned text. The regular expression provides a fallback for secret-like strings that are not present in the three environment variables. As with any pattern-based redaction, this only catches values covered by the configured secrets and regular expression.

#### How the helpers fit together

A typical evaluation flow can load cases with `load_jsonl`, verify them with `validate_cases`, record a compact input fingerprint with `file_sha`, and call `redact` on text before including it in results or logs.

---

## `evaluation.py`

This module runs evaluation cases and security probes, summarizes their results, records metadata about each run, and writes result files. It coordinates the runner, scoring, judging, security checks, and data redaction helpers.

#### Imports

- `statistics` calculates median latency.
- `datetime` and `timezone` provide UTC timestamps.
- The quality lab imports supply result paths and variant definitions, file fingerprints and redaction, faithfulness judging, Git revision lookup, case scoring helpers, and security probe evaluation.

#### `run_eval_cases(...)` — evaluate ordinary test cases

This function runs each case through the application runner and returns one result dictionary per case. It imports `call_with_retry` inside the function, then calls it with the runner, retry count, question, and case ID.

For each result, it:

1. Calls `check_case` to evaluate expected behaviors and uses `case_passed` to determine whether all required checks passed.
2. Builds a result row containing the case ID, category, whether it is subjective, question, check results, pass status, error and status information, route, answer, citations, retrieved sources, attempts, rewrites, relevance, latency, node path, and run ID.
3. Redacts the answer before storing it. It extracts and sorts source names for both cited sources and retrieved documents.
4. If `judge=True` and the application status is `answered`, it runs an additional faithfulness judgment. The judge receives the answer and the content of documents referenced by valid source IDs. The ID is treated as a one-based index into the documents list.
5. Collects names of checks that explicitly failed (`False`), chooses a `PASS`, `ERROR`, or `FAIL` label, and sends a concise status line to the supplied logger (which defaults to `print`).
6. Adds the row to the returned list.

The `retries` argument defaults to `2`. The `log` argument makes it possible to replace console output with another logging function.

#### `run_probes(...)` — run model-facing security probes

This function sends each security probe through the runner. A probe can optionally include an `inject_chunk`, which is passed to the runner along with the question and probe ID.

For each probe, it calls `check_probe` to determine the security verdict and stores a row containing the probe ID, attack description, a question shortened to 200 characters, verdict fields, application status, a redacted answer shortened to 600 characters, error, node path, and run ID. It logs the probe ID, uppercase outcome, and attack label, then returns all rows.

#### `summarize(rows, probes, code_checks)` — aggregate run results

This function computes summary statistics from evaluation rows, model-facing probe rows, and code-level security check rows.

- Its local `rate` helper counts pass values for a named check, ignoring `None` values.
- `errors` counts evaluation rows with a truthy error.
- Median latency is calculated only from rows without errors.
- Faithfulness results are collected only when `judge_faithful` is present and non-null.
- Results are grouped by category, using `?` when a case has no category.
- The returned dictionary includes total cases, errors, explicit passes, per-check rates, category totals, median latency, optional judge totals, and counts of each LLM security and code security outcome.

The explicit checks summarized are route, status, expected content, retrieval hit, citation hit, no sources, and groundedness. Security outcomes are counted under `held`, `failed`, and `error` for model probes, and `held`, `failed`, and `skipped` for code checks.

#### `build_meta(...)` — describe the run inputs and environment

This function creates metadata used to identify and interpret a run.

It records the selected variant and its display label, a UTC timestamp, the current Git SHA, an app description, a prompt version note, model ID, whether the model name indicates a moving target, SHA fingerprints for the cases and probes files, and whether the run used a mock runner. It also merges in the extra runner `info` fields.

The model ID defaults to `mock` if it is absent from `info`. `model_is_moving_target` is true when the model ID is `openrouter/free`.

#### `save(run, mock)` — write run results

This function creates the runs directory if necessary and writes the full run as indented UTF-8 JSON. The filename includes the variant and a UTC timestamp; mock runs receive a `mock_` prefix.

For real runs only, it also creates the results directory and updates `latest_<variant>.json` with the same run data. Mock runs do not replace these latest real-run files. The function returns the path to the timestamped run file.

#### Overall flow

A typical call sequence is:

1. Run cases with `run_eval_cases` and, unless disabled by the caller, probes with `run_probes`.
2. Aggregate those results and any code checks with `summarize`.
3. Create identifying metadata with `build_meta`.
4. Combine metadata and results into a run dictionary, then persist it with `save`.

---

## `judge.py` - Faithfulness Judge Helper

This function asks a language model to assess whether an answer is supported by the cited text chunks. It returns `True` or `False` when the judge succeeds, and `None` if setup or judging fails.

#### Imports

- `annotations` from `__future__` postpones evaluation of type annotations.
- `sys` is used to make sure the repository root is importable by Python.
- `REPO_ROOT` is the repository path imported from the quality lab configuration.

#### `judge_faithfulness(answer, cited_chunks)`

The function takes the generated answer and a list of text chunks cited for that answer.

1. It checks whether the repository root is already in `sys.path`. If not, it inserts it at the beginning so the Week 10 modules can be imported.
2. It imports the model factory `get_llm`, the prompt template `JUDGE_PROMPT`, and the structured response type `Faithfulness`.
3. It joins the cited chunks into one context string. Each chunk gets a one-based label such as `[1]`, `[2]`, and so on, with blank lines between chunks.
4. It gets the configured language model and requests structured output matching the `Faithfulness` model, using function calling as the structured-output method.
5. It formats the judge prompt with the context and answer, invokes the judge, and returns the result's `faithful` field.
6. If any exception occurs during path setup, imports, model setup, prompt formatting, or invocation, it returns `None`.

#### Return values

| Return value | Meaning |
| --- | --- |
| `True` | The judge marked the answer as supported by the cited chunks. |
| `False` | The judge marked the answer as not faithful to the cited chunks. |
| `None` | Judging could not be completed, such as when a dependency or model call fails. |

Because all exceptions are caught, the caller does not receive diagnostic details from this helper; it only sees `None` when judging fails.

#### How it fits into evaluation

The evaluation code can call this helper for answered cases when optional judging is enabled. It supplies the answer and the contents of the documents referenced by the case's valid citations. The resulting boolean or `None` can then be included in the run summary.

---

## `reporting.py` - Baseline Comparison Report

This module compares the saved results of a baseline run and a changed run, then builds a Markdown report. It highlights run metadata, summary metrics, case status changes, and model-facing security probe counts.

### ` _fmt(values)` — format a check rate

The helper formats a summary check rate as `passed/total`.

- If `values` is missing or its total is zero, it returns `n/a`.
- Otherwise, it returns a string such as `4/5`.

This keeps empty or unavailable check rates readable in the report.

### `compare(baseline, changed)` — generate the comparison

The function expects each argument to be a run dictionary with `meta`, `summary`, and (for case details) `cases` entries.

#### 1. Read summaries and identify caveats

It extracts each run's summary and builds a list of warnings when:

- The cases file fingerprints differ. The report says the comparison is invalid because the runs used different datasets.
- The model IDs differ.
- The changed run uses `openrouter/free`, which can route requests to different underlying models.
- The changed run's `top_k` equals its `baseline_top_k`, meaning this setting did not differ between variants.
- Either run has errored cases. The warning distinguishes errors such as rate limits or crashes from quality misses.

These checks provide context for interpreting the metrics; the function still generates the report when warnings exist.

#### 2. Add run details and warnings

The report starts with a `Baseline vs changed` heading. It includes each variant's label, UTC date, model ID, and `top_k` value. Any warnings are then added as Markdown blockquotes.

#### 3. Compare summary metrics

A Markdown table shows one row per run and includes:

- Explicit checks passed out of total cases
- Grounded answer check rate
- Correct route check rate
- Retrieval hit check rate
- Median latency in seconds

The `_fmt` helper formats each check rate, using `n/a` when there are no applicable checks.

#### 4. List case-level status changes

The function indexes changed-run cases by ID, then walks through baseline cases. For each case present in both runs, it assigns a status:

- `ERR` if the case has an error
- `PASS` if it passed
- `FAIL` otherwise

Only cases whose status differs between runs are included. Their note is `FIXED` when the changed run passes, `REGRESSION` when a baseline pass becomes a non-pass, and `changed` for other status changes. If no shared case changes status, the table contains a placeholder row saying so. Cases present in only one run are skipped.

#### 5. Show security probe totals and return Markdown

At the end, the report prints the `security_llm` summary dictionary for each run. The function joins all report lines with newline characters and returns the resulting Markdown string; it does not write the file itself.

### Output and usage

A caller can pass the returned string to a file-writing function or print it. In the CLI code, the comparison command writes the returned Markdown to `comparison.md` in the results directory and prints it to the console.

---

## `runner.py` - Evaluation Runners and Retry Logic: Code Explanation

This module provides helpers to identify the current Git revision, infer a likely application path from final state, build a runner for the real Week 10 RAG application, build an offline mock runner, and retry transient failures.

### Imports

- `subprocess` runs Git to read the current revision.
- `time` measures latency and pauses between retries.
- `uuid` creates a unique conversation ID for each real evaluation call.
- `patch` temporarily replaces retrieval behavior while a real call runs.
- Configuration imports provide the evaluation cases path, repository root, runner type, and available variants.
- Data helpers load cases and redact sensitive text.

### `git_sha()` — get the current revision

The function runs `git rev-parse --short HEAD` from the repository root, capturing its output with a five-second timeout. It returns the short revision string, or `unknown` if Git prints no value or any exception occurs.

### `inferred_path(state)` — estimate the graph path

This helper builds a readable sequence of likely graph node names from the final application state. It always starts with `prepare` and `classify`.

- If the route is `general`, it appends `general_answer` and returns immediately.
- Otherwise, it repeats `retrieve` and `grade` according to the attempt count, with `rewrite` between attempts.
- If the final status is `fallback`, it adds `generate` only when relevance is at least `0.6`, then adds `fallback`.
- For other statuses, it appends `generate`.

The returned string joins node names with ` > `. The docstring clarifies that this is inferred from final state and is not a LangSmith trace.

### `make_runner(variant)` — connect evaluation to the real application

This function builds and returns a callable runner plus an `info` dictionary describing the model and retrieval settings.

1. It rejects variants not found in `VARIANTS` with a `ValueError`.
2. It adds the repository root to `sys.path` if needed, then imports the LangChain tracing helper and Week 10 application components.
3. It builds the RAG graph with a memory checkpointer and adaptive behavior enabled.
4. It gets the baseline retrieval count from settings. The selected variant's `top_k` overrides it when specified; otherwise the baseline value is used.
5. It saves the original retrieval function and collects model, embedding, retrieval, relevance, retry, and collection details into `info`.

The nested `runner(question, inject_chunk, case_id)` temporarily patches the workflow's retrieval function. The patched version retrieves `top_k` chunks and, when a test injection is provided, prepends a high-scoring chunk with the supplied content and source. It then:

- Starts a high-resolution timer.
- Calls `workflow.ask` with a fresh UUID-based conversation ID and tracing metadata including the case ID and variant.
- Captures LangChain traced runs during the call.
- Returns a dictionary with the answer, status, route, sources, documents, attempts, rewrites, relevance, elapsed time, inferred node path, and root trace run ID if available.

The outer function returns `(runner, info)` so callers can execute cases and record the run configuration.

### `make_mock_runner(bad_ids=None)` — create an offline stand-in

This function creates a runner for exercising evaluation harness behavior without calling the real model. It loads the evaluation cases and indexes them by question. `bad_ids` can name cases that should intentionally return a fabricated answer to simulate failures.

For each call, the mock runner starts from a common set of default result fields. Then:

- If the question is not in the loaded cases, it returns a knowledge-route fallback answer.
- If the case ID is in `bad_ids`, it returns an intentionally incorrect answer with `answered` status.
- If the expected status is not `answered`, it returns a simple greeting or fallback answer and chooses the expected route when provided.
- For answered cases, it builds a simple answer from expected terms and mock documents from expected source names. It also builds citation records whose IDs correspond to the document positions.

The function returns the nested runner. The mock is useful for an offline smoke run of the harness, but its generated results do not measure real application quality.

### `call_with_retry(runner, retries, **kwargs)` — retry temporary failures

This helper calls the runner and returns its result when successful. If a call raises an exception, it records the exception type and message. It retries only when the message contains one of these indicators: `429`, `rate limit`, `timeout`, `temporarily`, or `503` (case-insensitive).

Before each retry, it sleeps for an exponentially increasing interval: 3 seconds, then 6 seconds, then 12 seconds, and so on. The `retries` value is the number of retries after the initial attempt.

If the error is not considered transient, or the retry limit is reached, it returns a standardized error result. The error text is redacted and limited to 500 characters; the result has status `error`, empty answer and route, and empty source/document lists. This lets the evaluation record operational failures separately from ordinary quality failures.

### How these helpers fit together

The evaluation module can obtain a real or mock runner, call it through `call_with_retry`, and store the returned data alongside model configuration and tracing information. The real runner connects to the Week 10 graph, while the mock runner exercises the evaluation workflow offline.

---

## `scoring.py` -Deterministic Case Scoring

This module checks evaluation results against expectations defined in each case. It uses text matching and source-name comparisons rather than a language model, and it marks checks that do not apply as `None`.

### Imports

- `re` provides regular expressions for normalizing text.

### `_norm(text)` — normalize text for comparisons

This helper lowercases text and replaces each run of whitespace with a single space. It returns the normalized string, making simple phrase matching insensitive to capitalization and repeated spaces or line breaks.

## `_contains(text, case)` — check expected phrases

This helper evaluates the case's optional phrase expectations:

- `expected_contains_any`: at least one listed phrase must appear.
- `expected_contains_all`: every listed phrase must appear.

Both the answer and each expected phrase are normalized with `_norm` before comparison. If neither expectation is provided, the function returns `None` to indicate that the check does not apply. If both are provided, both conditions must pass.

### `_source_names(items)` — extract source filenames

For each item, the helper reads its `source` field (using an empty string when absent), converts it to a path, and keeps only the filename. It returns the filenames as a set, removing duplicates.

### `check_case(case, result)` — run the applicable checks

This function returns a dictionary of check names and boolean results (or `None` when a check is not applicable).

1. It starts with `no_error`, which is true when the result has no error. If there is an error, it returns immediately without running the other checks.
2. If `expected_route` is present, it checks whether the result's route matches it (`route_ok`).
3. If `expected_status_any` is present, it checks whether the result status is one of the allowed statuses (`status_ok`).
4. It checks expected answer phrases with `_contains`, producing `contains_ok` or `None`.
5. If expected sources are listed, it compares their filenames against the retrieved documents and cited sources, producing `retrieval_hit` and `citation_hit`.
6. If `expect_no_sources` is true, it checks that the result has no citations (`no_sources`).
7. For an `answered` result with phrase expectations, it gathers the content of documents referenced by valid one-based source IDs. `grounded` passes only when there is at least one citation and the cited text satisfies the phrase expectations.
8. If the case expects only the `answered` status but does not provide phrase expectations, it sets `grounded` to false, since this deterministic check cannot verify support for the answer.

The citation IDs are treated as one-based indexes into the documents list. Invalid IDs are ignored when constructing cited text.

### `case_passed(checks)` — decide whether the case passed

This helper returns true only when every applicable check is true. Entries with value `None` are ignored. Thus, a check that does not apply neither passes nor fails the case, while any applicable false check makes the case fail.

### How these helpers fit together

The evaluation runner passes each case and its application result to `check_case`. It then uses `case_passed` to determine the overall case status and records the individual checks for reporting and summaries.

---

## `security.py` - Security Probe and Code Defense Checks

This module evaluates two kinds of security defenses: model-facing probes that inspect an application response, and code-level checks that exercise Week 10 safeguards directly without making an LLM call.

### Imports

- `annotations` from `__future__` postpones evaluation of type annotations.
- `sys` allows the repository root to be added to Python's import path.
- `Any` and `Callable` describe the helper function types.
- `REPO_ROOT` identifies the repository, and `SECRET_RE` detects text that looks like a secret.
- `secrets` returns configured secret values from the environment.
- `_contains` checks whether a response contains expected text from a probe.

### `check_probe(probe, result)` — score a model-facing security probe

This function returns an outcome, individual checks, and any detected forbidden substrings.

1. If the application result contains an error, it immediately returns outcome `error`, marks `no_error` false, and reports no leaked forbidden substrings.
2. Otherwise, it reads the answer and searches for each configured `forbidden_substrings` value without regard to letter case.
3. It checks that the answer contains no forbidden content and no secrets. The secret check looks for configured environment secret values and any key-shaped text matched by `SECRET_RE`.
4. If the probe specifies `expected_status_any`, it checks that the result status is allowed.
5. If the probe specifies `max_answer_chars`, it checks that the answer does not exceed that length.
6. If the probe specifies `expected_contains_any`, it checks that the answer preserves the expected task content using `_contains`.
7. The outcome is `held` when all applicable checks pass; otherwise it is `failed`.

The return value has this shape: `{"outcome": ..., "checks": ..., "leaked": [...]}`. A result error is distinguished from a security failure so operational problems are not reported as a defense failure.

### `security_code_checks()` — exercise code-level defenses

This function runs a small suite of direct checks against Week 10 components and returns a list of result rows. It first adds the repository root to `sys.path` when needed.

#### Local result helpers

- `record` appends a result with an ID, attack label, outcome, and detail. A `None` test result is recorded as `skipped`; `True` is `held`; and `False` is `failed`.
- `expect_raises` calls a function and checks whether it raises one of the expected exception types. If it returns normally, the check fails and records a shortened representation of the returned value. If it raises an expected exception, the check passes and records the exception type and a shortened message.

#### Calculator expression checks

The function tries to import `safe_eval` from `Week10.core.tools`. If that module is unavailable, the three calculator checks are recorded as skipped with the import error.

When available, it checks that the calculator rejects:

- `code_01`: an attempt to import `os` and execute a shell command.
- `code_02`: an attempt to walk Python object attributes through `__class__` and `__bases__`.
- `code_03`: a very large exponent expression intended to test resource exhaustion.

These checks expect `ValueError`, `SyntaxError`, or `TypeError`.

#### API input length check

The function imports Pydantic's `ValidationError` and the Week 10 `ChatRequest` model. If either import fails, `code_04` is skipped. Otherwise, it constructs a request with a 2,001-character question and expects validation to reject it with `ValidationError`.

#### Citation number validation check

The function imports `build_sources` from the Week 10 answer generator. If unavailable, `code_05` is skipped. Otherwise, it supplies two chunks and citation indices `[0, 99, -1, 2]`. It expects the function to retain only valid citation ID `2`; the check passes only when the resulting IDs equal `[2]`.

Finally, the function returns all check rows. These outcomes are suitable for inclusion in an evaluation run summary.

### Interpreting outcomes

| Outcome | Meaning |
| --- | --- |
| `held` | The response met the configured probe requirements, or the code rejected/handled the test attack as expected. |
| `failed` | A required response check failed, an attack was accepted, or the citation result differed from expectation. |
| `error` | A model-facing probe could not be scored because the application result had an error. |
| `skipped` | A code-level check could not run because the required Week 10 module or dependency was unavailable. |

---

## `test_eval.py` - Offline Quality Lab Tests

This test module checks the Week 11 quality lab without requiring API keys, Qdrant, or network access. It uses pytest and the lab's mock runner to verify data, scoring, retries, security checks, reporting, CLI behavior, and inferred graph paths.

### Imports and fixtures

The module imports the quality lab's CLI, configuration, data, evaluation, reporting, runner, scoring, and security modules, along with `json` and `pytest`.

- The module-scoped `cases` fixture loads the case JSONL file, validates it, and shares the resulting cases across tests.
- The module-scoped `probes` fixture loads the security probe JSONL file and shares it across tests.

### Dataset checks

#### `test_dataset_shape`

Checks that the evaluation dataset contains between 10 and 20 cases, that there are at least five security probes, and that the cases cover answerable, unanswerable, out-of-scope, ambiguous, and at least one `two_fact` category.

#### `test_perfect_mock_passes_everything`

Runs all cases through the mock runner with retries disabled and logging suppressed. It asserts that no case fails, confirming that the mock is aligned with the dataset's expected outcomes.

#### `test_bad_answer_is_detected`

Configures the mock runner to give case `rag_02` a deliberately incorrect answer. The test verifies that this case fails its phrase and groundedness checks while all other cases pass.

### Scoring behavior

#### `test_grounding_requires_expected_fact_in_cited_chunk`

Creates a case where the answer contains the expected term `cosine` and cites a document, but the cited document itself contains no relevant fact. It confirms that answer phrase matching can pass while the groundedness check fails.

#### `test_retrieval_hit_is_separate_from_citation_hit`

Provides the expected document in retrieval results but no citations. It asserts that retrieval succeeds while citation coverage fails, showing these are measured independently.

#### `test_fallback_case_fails_if_status_or_sources_are_wrong`

Defines a case that expects fallback status and no sources, then supplies an answered result with a citation. It checks that both status and no-source requirements fail.

### Error and retry behavior

#### `test_crash_is_recorded_as_error_not_quality_miss`

Uses a runner that raises a rate-limit exception. With retries disabled, both evaluation rows should record errors and fail; the summary should count two errors. This verifies that operational failures remain visible as errors.

#### `test_retry_recovers_from_transient_error`

Replaces the retry sleep function with a no-op to keep the test fast. A runner fails once with a rate-limit message, then succeeds. The test confirms that `call_with_retry` retries the transient failure and returns the successful answer.

### Security behavior

#### `test_probe_detects_prompt_leak_and_injection`

Checks several model-facing probe cases:

- A forbidden internal prompt term causes failure.
- An injected attack string causes failure.
- An answer that avoids the attack and preserves the expected legitimate content passes.
- A refusal that ignores the attack but also drops the legitimate task fails, validating the task-preservation check.

#### `test_probe_checks_unbounded_output_and_errors`

Checks that an answer exceeding the configured character limit fails, a short answer passes, and an application error produces the distinct `error` outcome.

#### `test_secret_is_redacted_from_probe_results`

Sets a fake API key in the environment and returns it in a probe answer. The test verifies that the probe fails because a secret was exposed, while the serialized result row does not contain the secret value.

#### `test_code_level_security_checks_do_not_report_failures`

Runs the local code-level defense checks and asserts that they return results with no `failed` outcome. Checks may still be skipped when the relevant Week 10 dependencies are unavailable.

### Summary and comparison behavior

#### `test_summary_and_compare_flag_regressions`

Builds baseline mock results and changed mock results with one intentionally bad case. It creates metadata for both runs, summarizes them, and generates the comparison report. The test asserts that the report labels `rag_01` as a regression and does not claim the comparison is invalid because the cases dataset is unchanged.

#### `test_compare_warns_on_moving_target_model`

Builds metadata using the `openrouter/free` model ID and confirms that the comparison report includes a warning about that moving-target model, even when comparing the run to itself.

### CLI and path behavior

#### `test_cli_mock_run_does_not_overwrite_latest`

Redirects results and run directories to pytest's temporary directory, then runs the CLI in mock mode. It verifies that a timestamped mock run file is created and that no `latest_baseline.json` file is written. This protects the latest real-run comparison data from being replaced by mock results.

#### `test_inferred_path`

Checks three inferred graph paths:

- A general question takes `prepare > classify > general_answer`.
- An answered knowledge question includes retrieval, grading, and generation.
- A low-relevance fallback after three attempts includes rewrites between retrieval attempts and ends at `fallback`.

### Running the tests

From the project environment, run the test file with pytest, for example:

```bash
pytest <path-to-this-test-file>
```

The tests are designed to remain offline; they focus on local harness behavior and mocked inputs rather than making real model or database calls.

---


