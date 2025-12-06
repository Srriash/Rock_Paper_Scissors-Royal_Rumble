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
BACKEND_API_BASE = os.getenv("BACKEND_API_BASE", "").rstrip("/")


def _has_backend():
    return bool(BACKEND_API_BASE)


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
    """Fetch a single player record by name from backend."""
    if not _has_backend() or not name:
        return None
    url = f"{BACKEND_API_BASE}/player"
    try:
        resp = requests.get(url, params={"name": name}, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data or None
    except Exception:
        return None


def upsert_score(name, matches_won, matches_lost, best_streak, win_pct=None):
    """Upsert a player's record via backend. Returns True on success, False otherwise."""
    if not _has_backend():
        return False
    url = f"{BACKEND_API_BASE}/score"
    payload = {
        "name": name,
        "matches_won": matches_won,
        "matches_lost": matches_lost,
        "best_streak": best_streak,
    }
    if win_pct is not None:
        payload["win_pct"] = win_pct
    try:
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        return True
    except Exception:
        return False
