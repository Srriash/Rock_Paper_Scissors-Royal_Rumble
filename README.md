# Rock Paper Scissors Royal Rumble

Neon arcade vibes, chiptune beats, and a smackdown of ROCK / PAPER / SCISSORS in Python.

## Why play this?
- Pygame retro UI with music and SFX; terminal mode for quick duels.
- Optional online leaderboard via your Cloudflare Worker proxy to Supabase (no keys in the client).
- Tested logic, tidy `src/` layout, ready-to-run assets.

## Quickstart
1) Install:
```powershell
python -m pip install -r requirements.txt
```
2) Launch (from repo root):
- Pygame UI:
  ```powershell
  set PYTHONPATH=src
  python -m rps.pygame_app
  ```
- Terminal duel:
  ```powershell
  set PYTHONPATH=src
  python -m rps.cli
  ```
- Compatibility: `python rps_pygame.py` also launches the Pygame UI.

## Pygame controls
- Click ROCK, PAPER, or SCISSORS to throw.
- `ESC` quits. Music toggles in-game. Audio loads from `assets/audio/`.

## Project layout
- `src/rps/logic.py` – rules and computer move picker
- `src/rps/cli.py` – terminal loop
- `src/rps/pygame_app.py` – main Pygame experience (music, SFX, leaderboard hooks)
- `src/rps/shared_scores.py` – backend proxy client (calls your Worker)
- `assets/audio/` – music and sound effects
- `data/scores.json` – local score cache (git-ignored)
- `tests/test_logic.py` – quick logic checks

## Leaderboard (backend proxy)
- Default: scores stay local unless `BACKEND_API_BASE` is set.
- To use a secure backend (Cloudflare Worker that talks to Supabase with your service-role key), set in `.env`:
  ```
  BACKEND_API_BASE=https://your-worker.yourdomain.workers.dev
  ```
  The client only calls your Worker; Supabase keys stay server-side. Server-side table can have generated columns like `win_pct` and `total_matches`; the client only sends name, matches_won, matches_lost, best_streak.

## Tests
```powershell
python -m pytest
```
or
```powershell
python tests/test_logic.py
```
