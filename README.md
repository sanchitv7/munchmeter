# MunchMeter

Voice-first calorie tracker — speak what you ate (including Hindi/Hinglish), get instant nutrition data logged automatically.

## Stack

- **Backend:** FastAPI + SQLite
- **Speech-to-Text:** Groq Whisper Large v3
- **LLM:** Google Gemini Flash (ingredient extraction)
- **Nutrition:** CalorieNinjas API

## Setup

```bash
cd backend
cp .env.example .env  # fill in API keys
uv sync
uv run uvicorn app.main:app --reload
```

Open `frontend/index.html` in browser.

## API Keys Required

- `GROQ_API_KEY` — https://console.groq.com
- `GOOGLE_API_KEY` — https://aistudio.google.com
- `CALORIENINJAS_API_KEY` — https://calorieninjas.com/api
