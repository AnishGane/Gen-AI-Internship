"""Discover which OpenRouter models are free AND support tool calling."""
import httpx
from Week9.agent.config import BASE_URL, FALLBACK_MODELS, ROUTER_MODEL, forced_model

def _is_zero(value) -> bool:
    try:
        return float(value) == 0.0
    except (TypeError, ValueError):
        return False

def fetch_free_tool_models(timeout: float = 15.0) -> list[dict]:
    """Return free models that list "tools" in supported_parameters.

    The /models endpoint is public, so no API key is needed here.
    """
    resp = httpx.get(f"{BASE_URL}/models", timeout=timeout)
    resp.raise_for_status()
    found = []
    for m in resp.json().get("data", []):
        pricing = m.get("pricing") or {}
        is_free = (
            m["id"].endswith(":free")
            and _is_zero(pricing.get("prompt"))
            and _is_zero(pricing.get("completion"))
        )
        supports_tools = "tools" in (m.get("supported_parameters") or [])
        if is_free and supports_tools:
            found.append(
                {
                    "id": m["id"],
                    "name": m.get("name", m["id"]),
                    "context_length": m.get("context_length") or 0,
                }
            )
    return sorted(found, key=lambda m: m["context_length"], reverse=True)

def pick_models(n: int = 3) -> list[str]:
    """Choose up to n model IDs, in priority order, for OpenRouter's fallback list.

    Order: OPENROUTER_MODEL override -> known-good IDs that are live today ->
    other live free tool models -> static fallback -> the free router.
    """
    override = forced_model()
    if override:
        return [override]

    try:
        live_ids = [m["id"] for m in fetch_free_tool_models()]
    except Exception as exc:  # network or API trouble: don't crash the lesson
        print(f"[models] live lookup failed ({exc}); using fallback list")
        live_ids = []

    preferred = [m for m in FALLBACK_MODELS if m in live_ids]
    others = [m for m in live_ids if m not in preferred]
    chosen = (preferred + others)[:n] or FALLBACK_MODELS[:n]
    if ROUTER_MODEL not in chosen and len(chosen) < n:
        chosen.append(ROUTER_MODEL)
    return chosen
