# Rock Paper Scissors Royal Rumble

## About
Retro deja vu in neon: chiptune soundtrack, chunky buttons, and a leaderboard that keeps your legacy. Your username anchors your stats, so every time you return you pick up exactly where you left off—no throwaway runs, just a climb to the top.

## Leaderboard
- Join a shared board with everyone who plays. Pick a unique username; your matches and streaks persist under that name.
- Scores travel through your backend proxy (Cloudflare Worker) to Supabase. Players never see your keys—only their ranks.

## How it works (under the hood)
- Game: Pygame front end for arcade visuals and sound; optional terminal mode for barebones duels.
- Backend: the client hits `BACKEND_API_BASE` (your Cloudflare Worker). The Worker upserts to Supabase using your service-role key with `on_conflict=name`.
- Data: Supabase stores wins, losses, best streak; generated columns (win_pct, total_matches) are computed in the DB.

## Use it
1) Install deps:
```powershell
python -m pip install -r requirements.txt
```
2) Set the backend (optional cloud scores) in `.env`:
```
BACKEND_API_BASE=https://your-worker.yourdomain.workers.dev
```
3) Run (from repo root):
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

Controls (Pygame): Click ROCK/PAPER/SCISSORS. `ESC` quits. Music toggles in-game. Audio lives in `assets/audio/`.

## Project layout
- `src/rps/logic.py` – rules and computer move picker
- `src/rps/cli.py` – terminal loop
- `src/rps/pygame_app.py` – main Pygame experience (music, SFX, leaderboard hooks)
- `src/rps/shared_scores.py` – client for the Cloudflare Worker backend
- `src/rps/gui_widgets.py` – small Pygame demo UI
- `assets/audio/` – music and sound effects
- `data/scores.json` – local score cache (git-ignored)
- `tests/test_logic.py` – quick logic checks
