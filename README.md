# Rock Paper Scissors Royal Rumble

## About
Retro-style Rock/Paper/Scissors with neon déjà vu vibes: chiptune soundtrack, chunky buttons, and a leaderboard that keeps your legacy. Create a unique username and your stats stick—every return is a climb, not a reset.

## Features
- Unique username: create it once; your stats persist under that name.
- Leaderboard: shared board for everyone; best streaks and matches tied to your name.
- Soundtrack: retro/war-style audio for the arcade mood.
- Chunky buttons: big, bold controls for visual punch.
- Website: a static page to navigate the module and setup.

## How it works (under the hood)
- Game: Pygame front end for arcade visuals and sound; optional terminal mode for barebones duels.
- Backend: the user hits `BACKEND_API_BASE` (Cloudflare Worker). The Worker upserts to Supabase with `on_conflict=name` so existing users update.
- Data: Supabase stores wins, losses, best streak; generated columns (`win_pct`, `total_matches`) are computed in the DB. Keep `name` UNIQUE and lowercased; RLS stays enabled if you use an anon key.
- Shared by default: the game points at the bundled Cloudflare Worker so players land on the shared board automatically.
  
## Use it
If you are using UV python, then prefix the commands with uv.
Otherwise, run the same commands without it.
1) Install deps:
   ```
   python -m pip install -r requirements.txt
   ```
   or
   ```
   python -m pip install requests
   python -m pip install pygame
   ```

3) Run (from repo root):
- Pygame UI:
```
# macOS / Linux
export PYTHONPATH=src

# Windows (CMD or PowerShell)
set PYTHONPATH=src

python -m rps.pygame_app
```

- Terminal duel:
 ```
 # macOS / Linux
export PYTHONPATH=src

# Windows
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
