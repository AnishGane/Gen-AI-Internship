from __future__ import annotations
import hashlib
import os
import json
from pathlib import Path
from Week11.quality_lab.config import SECRET_RE

def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{number} is not valid JSON: {exc}") from exc
    return rows

def validate_cases(cases: list[dict]) -> None:
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate case ids")
    for case in cases:
        if not case.get("id") or not case.get("question"):
            raise ValueError(f"case needs id and question: {case}")

def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]

def secrets() -> list[str]:
    names = ("OPENROUTER_API_KEY", "QDRANT_API_KEY", "LANGSMITH_API_KEY")
    return [value for name in names if (value := os.getenv(name))]

def redact(text: str) -> str:
    """Prevent known or key-shaped secrets from entering result files."""
    for secret in secrets():
        text = text.replace(secret, "[REDACTED]")
    return SECRET_RE.sub("[REDACTED]", text)