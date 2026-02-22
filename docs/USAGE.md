
# Usage Guide - Story Creator

## How to Run

### Full Stack (Recommended)
```bash
npm run dev
# Runs both Flask API (port 5000) and React frontend (port 3000)
```

### Backend/API Only
```bash
.venv\Scripts\python.exe api/main.py -i api
# API at http://localhost:5000
```

### Frontend Only
```bash
cd frontend
npm install  # First time only
npm run dev
# UI at http://localhost:3000
```

### Simulation Mode (Terminal)
```bash
.venv\Scripts\python.exe api/main.py -i simulation [--world-id <id> --character-id <id>]
```

## Features
- Create/manage worlds, stories, characters, locations, timelines
- Auto-generate content with GPT-4o-mini
- Visualize timelines, maps, relationships
- Interactive simulation (AI-driven)

## Testing
```bash
.venv\Scripts\python.exe api/test.py         # Core tests
.venv\Scripts\python.exe api/test_nosql.py   # NoSQL tests
.venv\Scripts\python.exe api/test_api_key.py # GPT API key check
```

## Storage
- Default: NoSQL (TinyDB, fast, single file)
- Optional: JSON (legacy, for debugging)

## Docs
- See `/docs/` for architecture, API, models, and more.
