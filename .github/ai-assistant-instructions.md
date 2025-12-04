# AI Assistant Instructions for Rock Paper Scissors Royal Rumble

## Project context
- Python project with Pygame UI and CLI. Source lives in `src/rps/`.
- Entrypoints: `python -m rps.pygame_app`, `python -m rps.cli`, or `python rps_pygame.py` (shim).
- Assets: audio under `assets/audio/`. Local data: `data/scores.json` (git-ignored).
- Tests in `tests/` (pytest). Set `PYTHONPATH=src` for imports.
- Optional Supabase leaderboard: use `SUPABASE_URL` and **public/anon** key only (e.g., `SUPABASE_ANON_KEY`). Never require or embed a service-role key.

## Do / Don't
- Do import from `rps.*` modules; keep paths relative to `src`.
- Do maintain compatibility with the existing file layout and README instructions.
- Do keep code ASCII, add comments only when needed for clarity.
- Don’t hardcode secrets or service-role keys; assume `.env` values.
- Don’t move assets out of `assets/audio/` or data out of `data/` without a clear reason.

## Style and testing
- Follow current patterns; keep Pygame UI behavior intact.
- Prefer small, clear functions; avoid needless globals.
- If adding logic, add/adjust tests in `tests/` and keep pytest usage.
