from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Callable

LAB_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = Path(os.environ.get("GENAI_REPO_ROOT", LAB_DIR.parent)).resolve()
DATA_DIR = LAB_DIR / "data"
RESULTS_DIR = LAB_DIR / "results"
RUNS_DIR = RESULTS_DIR / "runs"
CASES_PATH = DATA_DIR / "eval_cases.jsonl"
PROBES_PATH = DATA_DIR / "security_probes.jsonl"

# Compare one intentional change: retrieval count. Baseline uses Week 10 settings.top_k.
VARIANTS: dict[str, dict[str, Any]] = {
    "baseline" : {"top_k": None, "label": "Week 10 agentic RAG as committed (settings.top_k)"},
    "changed" : {"top_k": 6, "label": "Same app, retrieval top_k raised to 6"}
}

Runner = Callable[..., dict]
SECRET_RE = re.compile(r"(sk-or-[A-Za-z0-9_\-]{10,}|lsv2_[A-Za-z0-9_\-]{10,})")