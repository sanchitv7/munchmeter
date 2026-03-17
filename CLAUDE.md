# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Always run from `backend/` with the venv active:

```bash
cd backend

# Install / sync deps
uv sync

# Run dev server
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_meals.py::test_create_meal -v
```

## Architecture

**Pipeline:** `audio → POST /api/transcribe → POST /api/extract-ingredients → POST /api/nutrition-lookup → POST /api/meals`

Each step is a standalone endpoint so the frontend can chain them and display intermediate results.

### Backend (`backend/app/`)

| File | Role |
|------|------|
| `main.py` | FastAPI app, CORS, lifespan hook calls `init_db()`, mounts frontend static files |
| `config.py` | `Settings` via `pydantic-settings`, reads `.env` |
| `database.py` | `aiosqlite` helpers: `init_db()` creates schema, `get_db()` FastAPI dependency |
| `models.py` | All Pydantic request/response models shared across routers |
| `routers/transcribe.py` | `POST /api/transcribe` — multipart audio → text |
| `routers/extract.py` | `POST /api/extract-ingredients` — text → `[{ingredient, quantity, unit}]` |
| `routers/nutrition.py` | `POST /api/nutrition-lookup` — ingredient list → per-item nutrition + totals |
| `routers/meals.py` | `POST /api/meals`, `GET /api/meals?date=YYYY-MM-DD` |
| `services/whisper.py` | Groq AsyncGroq client, `whisper-large-v3` |
| `services/ingredient_parser.py` | Gemini Flash structured output, Hindi/Hinglish normalisation |
| `services/nutrition.py` | CalorieNinjas natural-language API; fallback to Open Food Facts |

### Database (SQLite)

Two tables: `meal_logs` (one row per meal slot per day) and `meal_log_items` (one row per ingredient, FK to `meal_logs`).

### Frontend (`frontend/index.html`)

Single HTML page (no build step). Uses `MediaRecorder` API to capture audio, then chains the four API calls and renders results. Served by FastAPI at `/` via `StaticFiles`.

## Environment

Copy `backend/.env.example` → `backend/.env` and fill in:
- `GROQ_API_KEY`
- `GOOGLE_API_KEY`
- `CALORIENINJAS_API_KEY`
