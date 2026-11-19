import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://openrouter.ai/api/v1"

# Free model IDs change often. These are only a *fallback* list used when the
# live lookup in models.py fails. Run `python -m scripts.list_free_models`
# to see what is free and tool-capable today.
FALLBACK_MODELS = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3.5-lightning:free",
]

# A router that picks any free model able to handle the request (tools included).
ROUTER_MODEL = "openrouter/free"

def get_api_key() -> str:
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit(
            "OPENROUTER_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return key

def forced_model() -> str | None:
    """Optional override: OPENROUTER_MODEL in .env."""
    return os.getenv("OPENROUTER_MODEL") or None
