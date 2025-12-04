import os
import requests


def _load_dotenv():
    """Lightweight .env loader so the game works even when env vars aren't pre-set."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
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

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE", "")
TABLE = "scores"


def _headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def fetch_leaderboard(limit=10):
    """Fetch top streaks from Supabase. Returns list of dicts or empty list on failure."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    url = f"{SUPABASE_URL}/rest/v1/{TABLE}?select=*&order=best_streak.desc&limit={limit}"
    try:
        resp = requests.get(url, headers=_headers(), timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def fetch_player(name):
    """Fetch a single player record by name."""
    if not SUPABASE_URL or not SUPABASE_KEY or not name:
        return None
    url = f"{SUPABASE_URL}/rest/v1/{TABLE}?name=eq.{name}&select=*"
    try:
        resp = requests.get(url, headers=_headers(), timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data[0] if data else None
    except Exception:
        return None


def upsert_score(name, matches_won, matches_lost, best_streak, win_pct=None):
    """Upsert a player's record. Returns True on success, False otherwise."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    url = f"{SUPABASE_URL}/rest/v1/{TABLE}"
    payload = {
        "name": name,
        "matches_won": matches_won,
        "matches_lost": matches_lost,
        "best_streak": best_streak,
    }
    if win_pct is not None:
        payload["win_pct"] = win_pct
    try:
        resp = requests.post(
            url,
            headers=_headers(),
            json=payload,
            timeout=5,
            params={"on_conflict": "name"},
        )
        resp.raise_for_status()
        return True
    except Exception:
        return False
