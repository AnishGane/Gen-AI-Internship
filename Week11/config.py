from pathlib import Path

class Config:
    lab_dir = Path(__file__).resolve().parent
    repo_dir = lab_dir.parent.parent # repo root, so we can import files from `Week10`
    data_dir = lab_dir / "data"
    results_dir = lab_dir / "results"
    run_dir = results_dir / "runs"

    cases_path = data_dir / "eval_cases.jsonl"
    probes_path = data_dir / "security_probes.jsonl"

config = Config()