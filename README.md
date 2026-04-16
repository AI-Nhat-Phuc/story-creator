# Story Creator

An interactive storytelling platform with a **React frontend** and **Flask API backend**, deployed as a monorepo on **Vercel**. Integrates GPT-4o-mini for AI-powered character simulation and content generation.

**Live**: https://story-creator-cyan.vercel.app

---

## Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | [/](https://story-creator-cyan.vercel.app/) | Home — system overview |
| Worlds | [/worlds](https://story-creator-cyan.vercel.app/worlds) | Browse and manage worlds |
| Stories | [/stories](https://story-creator-cyan.vercel.app/stories) | Browse and manage stories |
| Login | [/login](https://story-creator-cyan.vercel.app/login) | Sign in |
| Register | [/register](https://story-creator-cyan.vercel.app/register) | Create an account |
| Admin | [/admin](https://story-creator-cyan.vercel.app/admin) | System administration (admin only) |
| Facebook Manager | [/facebook](https://story-creator-cyan.vercel.app/facebook) | Manage Facebook Page posts (requires key) |
| Facebook Token | [/facebook-token](https://story-creator-cyan.vercel.app/facebook-token) | Retrieve your Facebook access token |
| API Docs | [/api/docs](https://story-creator-cyan.vercel.app/api/docs) | Swagger UI |

---

## Features

- Create and manage worlds across genres: Fantasy, Sci-Fi, Modern, Historical
- Write stories with automatic character detection and smart cross-story linking
- Rich text story editor with formatting toolbar
- Manage characters with attributes (Strength, Intelligence, Charisma)
- Track locations with coordinates
- Timeline visualization using the light cone (time cone) model
- Stories auto-link when they share characters, locations, or time periods
- GPT-4o-mini: generate world descriptions, analyze characters, simulate decisions
- Swagger UI for interactive API documentation
- Deployed on Vercel — static frontend + serverless Python API

---

## Quick Start

### Requirements

- Python 3.10+
- Node.js 18+
- OpenAI API key (optional — only needed for GPT features)

### Install

```bash
git clone https://github.com/your-username/story-creator.git
cd story-creator

# Create Python virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1       # Windows PowerShell
# source .venv/bin/activate      # macOS/Linux

# Install all dependencies (backend + frontend)
npm run install:all
```

### Configure (optional)

```bash
# Copy and edit environment variables
cp .env.example .env
# Add your keys to .env
```

Key variables:

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | GPT features |
| `GOOGLE_CLIENT_ID` | Google OAuth |
| `FACEBOOK_APP_ID` | Facebook OAuth |
| `JWT_SECRET` | Token signing |
| `MONGODB_URI` | MongoDB (optional, for persistent storage) |

### Run

```bash
# Start full stack (recommended)
npm run dev

# Or start separately:
# Terminal 1 — API (port 5000)
.venv\Scripts\python.exe api/main.py -i api

# Terminal 2 — Frontend (port 3000)
cd frontend && npm run dev
```

Access:
- React UI: http://localhost:3000
- API Swagger: http://localhost:5000/api/docs

---

## Project Structure

```
story-creator/
├── api/                          # Python Flask backend
│   ├── app.py                    # Vercel serverless entrypoint
│   ├── main.py                   # Local development entrypoint
│   ├── requirements.txt
│   ├── ai/                       # GPT-4o-mini integration
│   ├── core/
│   │   ├── models/               # Domain models (World, Story, Entity, Location, TimeCone)
│   │   ├── exceptions.py         # Custom exception hierarchy (APIException subclasses)
│   │   └── permissions.py        # Role/permission definitions
│   ├── generators/               # Content generators and story linker
│   ├── interfaces/               # Flask app + blueprint routes
│   │   ├── api_backend.py        # Flask app factory + route registration
│   │   ├── auth_middleware.py    # @token_required, @admin_required decorators
│   │   ├── error_handlers.py     # Global exception → JSON response mapping
│   │   ├── simulation_interface.py
│   │   └── routes/               # world, story, auth, gpt, event routes
│   ├── schemas/                  # Marshmallow validation schemas
│   ├── services/                 # Business logic (GPTService, AuthService, ...)
│   ├── storage/                  # TinyDB (default) and MongoDB backends
│   ├── utils/
│   │   ├── responses.py          # success_response, created_response, paginated_response
│   │   └── validation.py         # @validate_request, @validate_query_params decorators
│   └── visualization/            # Relationship diagrams
│
├── frontend/                     # React application
│   ├── e2e/                      # Playwright end-to-end tests
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   │   └── storyEditor/      # Story editor (NovelEditor, FormattingToolbar, ...)
│   │   ├── containers/           # Data-fetching containers
│   │   ├── contexts/             # AuthContext, GptTaskContext
│   │   ├── hooks/                # useKeepAlive, and other custom hooks
│   │   ├── pages/                # Dashboard, Worlds, Stories, detail pages
│   │   ├── services/api.js       # Centralized Axios API client
│   │   └── App.jsx               # Root component + React Router
│   ├── playwright.config.cjs
│   ├── vite.config.js
│   └── package.json
│
├── docs/                         # Documentation
├── vercel.json                   # Vercel deployment config
├── package.json                  # Root npm scripts
└── .env                          # Environment variables (not committed)
```

> **Note:** All Python code lives in `api/`. Internal imports use bare module names — `from core.models import World`, not `from api.core.models import World`.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/worlds` | List all worlds |
| POST | `/api/worlds` | Create a world |
| GET | `/api/worlds/<id>` | Get world details |
| GET | `/api/worlds/<id>/characters` | List characters in a world |
| GET | `/api/worlds/<id>/relationships` | Relationship graph |
| POST | `/api/stories` | Create a story |
| GET | `/api/stories/<id>` | Get story details |
| POST | `/api/gpt/analyze` | Trigger GPT analysis (async) |
| GET | `/api/gpt/results/<task_id>` | Poll GPT result |
| GET | `/api/stats` | System statistics |

Full interactive docs: http://localhost:5000/api/docs

---

## Deploy to Vercel

```bash
npm i -g vercel
vercel          # preview deploy
vercel --prod   # production deploy
```

**How it works** (`vercel.json`):
- Builds the React frontend (`cd frontend && npm run build`)
- Serves `frontend/dist` as static files
- Routes `/api/*` to `api/app.py` as a Python serverless function
- Default storage: TinyDB at `/tmp/story_creator.db` (ephemeral per instance)
- For persistent storage, set `MONGODB_URI` to use MongoDB instead

---

## Testing

### Backend unit tests

```bash
.venv\Scripts\python.exe api/test.py                   # Core functionality
.venv\Scripts\python.exe api/test_nosql.py             # NoSQL storage
.venv\Scripts\python.exe api/test_api_key.py           # API key validation
.venv\Scripts\python.exe api/test_api.py               # API integration
.venv\Scripts\python.exe api/test_permissions.py       # Permission system
.venv\Scripts\python.exe api/test_collaboration.py     # Collaboration features
.venv\Scripts\python.exe api/test_novel.py             # Novel editor
.venv\Scripts\python.exe api/test_story_editor.py      # Story editor
.venv\Scripts\python.exe api/test_cold_start.py        # API cold-start behavior
.venv\Scripts\python.exe api/test_world_publish_mode.py # World publish mode
```

### Playwright E2E tests

```bash
cd frontend
npx playwright test                  # Run all E2E tests
npx playwright test e2e/login.spec.cjs        # Login flow
npx playwright test e2e/storyEditor.spec.cjs  # Story editor flow
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite 5, TailwindCSS 3.4 + DaisyUI 4.6, React Router 6, Axios |
| Backend | Flask 3.0, TinyDB / MongoDB, OpenAI (GPT-4o-mini), PyJWT, Marshmallow, Flasgger |
| Auth | Google OAuth, Facebook OAuth, JWT sessions |
| Testing | pytest (backend), Playwright (E2E) |
| Deploy | Vercel (static + serverless) |

---

## How Stories Link

Stories automatically link when they share:

1. **Characters** — the same entity appears in multiple stories
2. **Locations** — stories take place in the same location
3. **Time** — time cones are close to each other

This uses inverted indices (`{entity_id: [story_ids]}`) for efficient graph building.

## Auto World Selection

When creating a story, the system picks a default world based on the story genre:

| Genre | Default World |
|-------|--------------|
| Adventure | Fantasy World |
| Mystery | Modern World |
| Conflict | Historical World |
| Discovery | Sci-Fi World |

## GPT Simulation Mode

```bash
.venv\Scripts\python.exe api/main.py -i simulation
```

Simulates characters making decisions inside a story. At each step:
- 3 choices: act / oppose / retreat
- Non-player characters are controlled by GPT
- Responses are auto-translated English → Vietnamese

---

## VS Code Tasks

Pre-configured tasks in `.vscode/tasks.json`:

| Task | Description |
|------|-------------|
| `Full Stack Dev` | Run API + frontend together |
| `Run API Backend` | Flask API on port 5000 |
| `Run React Frontend` | Vite dev server on port 3000 |
| `Run Tests` / `Run NoSQL Tests` | Test suites |
| `Build React` | Production frontend build |

---

## Documentation

Additional guides in `docs/`:

- [API Documentation](docs/API_DOCUMENTATION.md)
- [Architecture](docs/architecture_diagram.md)
- [Models Guide](docs/MODELS_GUIDE.md)
- [Storage Guide](docs/STORAGE_GUIDE.md)
- [GPT Integration](docs/GPT_INTEGRATION_GUIDE.md)
- [React Architecture](docs/REACT_ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT_GUIDE.md)

---

## License

MIT
