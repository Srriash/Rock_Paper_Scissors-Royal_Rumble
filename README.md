# Rock Paper Scissors Royal Rumble

Retro, arcade-style Rock-Paper-Scissors built in Python with both a CLI and a Pygame experience.

## Setup
```powershell
python -m pip install -r requirements.txt
```
Optional: create and activate a virtual environment before installing. If you are running directly from the repo, set the source folder on your path first:
```powershell
set PYTHONPATH=src
```

## Run the games
- Pygame retro UI:
  ```powershell
  python -m rps.pygame_app
  ```
- Simple terminal game:
  ```powershell
  python -m rps.cli
  ```
- Minimal sample UI helper: `python -m rps.gui_widgets` (used as a demo component).

## Project layout
- `src/rps/logic.py` — core game rules (determine winner, random CPU move)
- `src/rps/cli.py` — terminal-based game loop
- `src/rps/pygame_app.py` — main Pygame experience with sounds and leaderboard hooks
- `src/rps/gui_widgets.py` — lightweight Pygame UI demo
- `src/rps/shared_scores.py` — Supabase leaderboard helpers
- `assets/audio/` — music and sound effects
- `data/scores.json` — local score cache (ignored by git)
- `tests/test_logic.py` — quick logic checks

## Leaderboard (optional)
If you want to sync scores to Supabase, set these in a `.env` at the repo root:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE=service-role-key
```
Without these, the game still runs; leaderboard features quietly no-op.

## Controls (Pygame)
- Click ROCK, PAPER, or SCISSORS to play rounds.
- Press `ESC` to quit. Music toggles in-game; sounds auto-load from `assets/audio/`.

## Tests
Run the quick checks:
```powershell
python -m pytest
```
or
```powershell
python tests/test_logic.py
```

