# Rock Paper Scissors Royal Rumble

> Neon-lit arcade vibes, chiptune beats, and a smackdown of ROCK / PAPER / SCISSORS.

## ✨ Why play this?
- 🕹️ Pygame retro UI with music + SFX, tuned for quick duels.
- ⌨️ Terminal mode for minimalists.
- 🌐 Optional online leaderboard (your Supabase, anon key only).
- ✅ Tested logic, tidy `src/` layout, and ready-to-run assets.

## 🚀 Quickstart
1) Install:
```powershell
python -m pip install -r requirements.txt
```
2) Launch (from repo root):
- Pygame UI
  ```powershell
  set PYTHONPATH=src
  python -m rps.pygame_app
  ```
- Terminal duel
  ```powershell
  set PYTHONPATH=src
  python -m rps.cli
  ```
- Compatibility: `python rps_pygame.py` also launches the Pygame UI.

## 🎮 Pygame controls
- Click ROCK, PAPER, or SCISSORS to throw.
- `ESC` quits. Music toggles in-game. Audio loads from `assets/audio/`.

## 🧭 Project layout
- `src/rps/logic.py` – rules and computer move picker
- `src/rps/cli.py` – terminal loop
- `src/rps/pygame_app.py` – main Pygame experience (music, SFX, leaderboard hooks)
- `src/rps/gui_widgets.py` – small Pygame demo UI
- `src/rps/shared_scores.py` – optional Supabase client
- `assets/audio/` – music and sound effects
- `data/scores.json` – local score cache (git-ignored)
- `tests/test_logic.py` – quick logic checks

## 🌐 Leaderboard (optional)
- Default: scores stay local; cloud sync is off.
- If you want shared scores, set up your own Supabase project and add to `.env`:
  ```
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_ANON_KEY=your-anon-key
  ```
  Use only a public/anon key with strict RLS. Do not share a service-role key. Update `src/rps/shared_scores.py` to read the anon key if you enable this.

## ✅ Tests
```powershell
python -m pytest
```
or
```powershell
python tests/test_logic.py
```
