# MunchMeter

Voice-first calorie tracker — speak what you ate (including Hindi/Hinglish), get instant nutrition data logged automatically.

## Stack

- **Backend:** FastAPI + SQLite
- **Speech-to-Text:** Groq Whisper Large v3
- **LLM:** Google Gemini Flash (ingredient extraction)
- **Nutrition:** USDA FoodData Central API

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
- `GEMINI_API_KEY` — https://aistudio.google.com
- `USDA_API_KEY` — optional, defaults to `DEMO_KEY` (https://fdc.nal.usda.gov/api-guide.html)
