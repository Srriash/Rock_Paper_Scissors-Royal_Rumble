import os
from pathlib import Path
import requests


def _load_dotenv():
    """Lightweight .env loader so the game works even when env vars aren't pre-set."""
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    try:
        with env_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k and v and k not in os.environ:  # don't override existing
                    os.environ[k] = v
    except Exception:
        # best-effort: ignore failures
        pass


_load_dotenv()

# Public-facing backend API that proxies to Supabase securely (no keys in client)
# Default to the shared Worker so users don't need to set anything.
BACKEND_API_BASE = os.getenv(
    "BACKEND_API_BASE",
    "https://floral-frog-3f5f.sriashwinsridharan.workers.dev",
).rstrip("/")


def _has_backend():
    return bool(BACKEND_API_BASE)


def _normalize_name(name: str) -> str:
    return (name or "").strip().lower()


def fetch_leaderboard(limit=10):
    """Fetch top streaks from a secure backend. Returns list of dicts or empty list on failure."""
    if not _has_backend():
        return []
    url = f"{BACKEND_API_BASE}/leaderboard"
    try:
        resp = requests.get(url, params={"limit": limit}, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def fetch_player(name):
    """Fetch a single player record by name from backend. Returns a dict or None."""
    if not _has_backend() or not name:
        return None
    name = _normalize_name(name)
    url = f"{BACKEND_API_BASE}/player"
    try:
        resp = requests.get(url, params={"name": name}, timeout=5)
        if resp.status_code >= 400:
            return None
        data = resp.json()
        if isinstance(data, list):
            return data[0] if data else None
        return data or None
    except Exception:
        return None


def upsert_score(name, matches_won, matches_lost, best_streak):
    """Upsert a player's record via backend. Returns the saved record or None.

    Note: win_pct/total_matches are computed in the DB, so we do not send them.
    """
    if not _has_backend():
        return None
    name = _normalize_name(name)
    url = f"{BACKEND_API_BASE}/score"
    payload = {
        "name": name,
        "matches_won": matches_won,
        "matches_lost": matches_lost,
        "best_streak": best_streak,
    }
    try:
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code >= 400:
            return None
        # try to parse json; if not available, treat as success with no body
        data = resp.json()
        if isinstance(data, list):
            return data[0] if data else None
        return data or None
    except Exception:
        return None
