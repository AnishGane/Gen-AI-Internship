# Baseline vs changed

- Baseline: `Week 10 agentic RAG as committed (settings.top_k)` (2026-11-22T08:05:22+00:00, model `openrouter/free`, top_k=4)
- Changed: `Same app, retrieval top_k raised to 6` (2026-11-22T08:00:35+00:00, model `openrouter/free`, top_k=6)

> Warning: Runs used `openrouter/free`, which may route to different models; use a fixed model ID for fair comparison.
> Warning: Errored cases: baseline=16, changed=15; rate limits and crashes are not quality misses.

| Version | Explicit checks passed | Grounded answers | Route correct | Retrieval hit | Median latency |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 0/17 | 0/1 | 0/1 | 0/1 | 5.15s |
| Changed | 0/17 | 0/2 | 0/1 | 0/2 | 10.96s |

## Case-level differences

| Case | Category | Baseline | Changed | Note |
| --- | --- | --- | --- | --- |
| amb_17 | ambiguous | ERR | FAIL | changed |

## Security probes (LLM-facing)

- Baseline: {'held': 0, 'failed': 0, 'error': 8}
- Changed: {'held': 3, 'failed': 0, 'error': 5}
