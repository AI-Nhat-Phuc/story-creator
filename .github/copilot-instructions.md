# Story Creator - AI Agent Instructions

## Project Overview
Interactive storytelling system that generates interconnected fictional worlds, stories, characters, and locations. Features GPT-4o-mini integration for character simulation and content generation with clean service layer architecture.

**Deployed as Vercel monorepo**: React frontend (static) + Python API (serverless functions).

## Monorepo Structure

```
story-creator/
├── api/                          # 🐍 All Python backend code
│   ├── app.py                    # Vercel serverless entrypoint
│   ├── main.py                   # Local dev entrypoint
│   ├── requirements.txt          # Python dependencies
│   ├── ai/                       # AI integration
│   │   ├── gpt_client.py         # OpenAI GPT-4o-mini client
│   │   ├── prompts.py            # Prompt templates
│   │   └── simulation.py         # Simulation logic
│   ├── core/models/              # Domain models
│   │   ├── world.py
│   │   ├── story.py
│   │   ├── entity.py
│   │   ├── location.py
│   │   └── time_cone.py
│   ├── generators/               # Content generators
│   │   ├── world_generator.py
│   │   ├── story_generator.py
│   │   └── story_linker.py
│   ├── interfaces/               # Flask API
│   │   ├── api_backend.py        # Main Flask app + CORS + Swagger
│   │   ├── simulation_interface.py
│   │   └── routes/               # Blueprint routes
│   │       ├── world_routes.py
│   │       ├── story_routes.py
│   │       ├── gpt_routes.py
│   │       ├── health_routes.py
│   │       └── stats_routes.py
│   ├── services/                 # Business logic layer
│   │   ├── gpt_service.py
│   │   └── character_service.py
│   ├── storage/                  # Storage backends
│   │   ├── nosql_storage.py      # TinyDB (default)
│   │   ├── json_storage.py       # File-based (legacy)
│   │   └── base_storage.py
│   └── visualization/
│       └── relationship_diagram.py
│
├── frontend/                     # ⚛️ React application
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   ├── components/           # Reusable UI components
│   │   │   ├── GptButton.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── Modal.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── Toast.jsx
│   │   │   ├── storyTemplates.js
│   │   │   ├── stories/StoriesView.jsx
│   │   │   ├── storyDetail/StoryDetailView.jsx
│   │   │   └── worldDetail/WorldDetailView.jsx, WorldTimeline.jsx
│   │   ├── containers/           # Data/logic containers
│   │   ├── layouts/MainLayout.jsx
│   │   ├── pages/                # Route pages
│   │   │   ├── Dashboard.jsx
│   │   │   ├── WorldsPage.jsx
│   │   │   ├── WorldDetailPage.jsx
│   │   │   ├── StoriesPage.jsx
│   │   │   └── StoryDetailPage.jsx
│   │   └── services/api.js       # Axios API client
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── docs/                         # 📖 Documentation
├── vercel.json                   # Vercel monorepo config
├── package.json                  # Root npm scripts (concurrently)
├── .env                          # Environment variables (OPENAI_API_KEY)
└── .github/
    └── copilot-instructions.md   # This file
```

**IMPORTANT**: All backend Python code lives inside `api/`. Imports within `api/` do NOT use `api.*` prefix — they use bare module names (e.g., `from core.models import World`, `from storage import NoSQLStorage`). This is because:
- **Vercel**: `api/` is the function root, so `api/` is automatically on `sys.path`
- **Local dev**: `api/app.py` and `api/main.py` both do `sys.path.insert(0, os.path.dirname(__file__))` to add `api/` to the path

## Architecture

### Vercel Deployment (Production)

**Config** (`vercel.json`):
```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "echo skip",
  "framework": null,
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/app.py" }
  ]
}
```

- **Frontend**: Built by Vite, served as static files from `frontend/dist`
- **API**: `api/app.py` is the serverless function entrypoint. Vercel auto-detects Python functions in `api/`
- **Database**: TinyDB writes to `/tmp/story_creator.db` on Vercel (read-only filesystem)
- **CORS**: Dynamically adds `VERCEL_URL` to allowed origins
- **Environment Variables**: Set `OPENAI_API_KEY` in Vercel dashboard for GPT features

**Entrypoint** (`api/app.py`):
```python
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interfaces.api_backend import APIBackend
db_path = os.environ.get("STORY_DB_PATH",
    "/tmp/story_creator.db" if os.environ.get("VERCEL") else "story_creator.db")
api = APIBackend(db_path=db_path)
app = api.app  # Exposed for Vercel/WSGI
```

### Service Layer (`api/services/`)
**Business logic separated from UI** — Services handle all complex operations:
- **GPTService** (`gpt_service.py`): GPT operations with threading and callbacks
  - `generate_world_description()`, `generate_story_description()`, `is_available()`
- **CharacterService** (`character_service.py`): Character management utilities (static methods)
  - `detect_mentioned_characters()`, `get_character_names()`, `format_character_display()`

**Pattern**: Services use callback pattern for async operations, Flask routes never touch business logic directly.

### Core Domain Models (`api/core/models/`)
- **World**: Container for stories, locations, entities. Has `world_type` (fantasy/sci-fi/modern/historical)
- **Story**: Narrative content with genre, linked to entities/locations via ID lists
- **Entity**: Characters with attributes (Strength, Intelligence, Charisma) and `entity_type`
- **Location**: Physical places with coordinates (x, y)
- **TimeCone**: Temporal context binding stories to timeline indices

All models follow pattern: `to_dict()`, `to_json()`, `from_dict()`, `from_json()` for serialization.

### Storage Layer (`api/storage/`)
**Dual storage backends** — default is NoSQL for performance:
- **NoSQLStorage** (`nosql_storage.py`): TinyDB-based, single file database. Use `Query()` for filtering.
- **JSONStorage** (`json_storage.py`): File-based JSON storage, legacy option.

**On Vercel**: Database path must be `/tmp/` (read-only filesystem). Data is ephemeral per invocation.

### Generators (`api/generators/`)
- **WorldGenerator**: Creates worlds from prompts, auto-generates locations/entities
- **StoryGenerator**: Generates stories with genre-specific templates
- **StoryLinker**: Links stories by shared entities, locations, or time using graph algorithms

### REST API (`api/interfaces/`)
- **api_backend.py**: Main Flask app with CORS, Swagger, blueprint registration
- **routes/**: Modular Flask blueprints:
  - `world_routes.py`: GET/POST `/api/worlds`, GET `/api/worlds/<id>`, characters, relationships
  - `story_routes.py`: POST `/api/stories`, GET `/api/stories/<id>`
  - `gpt_routes.py`: POST `/api/gpt/analyze`, GET `/api/gpt/results/<task_id>`
  - `health_routes.py`: GET `/api/health`
  - `stats_routes.py`: GET `/api/stats`

### Frontend (`frontend/`)
- **React 18** + **Vite 5** + **TailwindCSS 3.4** + **DaisyUI 4.6**
- `services/api.js`: Centralized Axios client. API_BASE_URL:
  - Production: `/api` (same Vercel domain, hits rewrites)
  - Development: `http://localhost:5000/api`
- Component architecture: Pages → Containers → Views/Components

## GPT Integration (`api/ai/gpt_client.py` + `api/services/gpt_service.py`)

**Environment Setup**: Requires `OPENAI_API_KEY` in `.env` file (or Vercel env vars)

**Model**: `gpt-4o-mini`

Key methods in GPTIntegration:
- `translate_eng_to_vn(text)`: Auto-translation for simulation mode
- `generate_character_decision(character_name, situation, story_context, character_traits)`: AI decides character actions

**Service Layer Usage** (PREFERRED):
```python
self.gpt_service = GPTService(self.gpt)
self.gpt_service.generate_world_description(
    world_type="fantasy",
    callback_success=self._on_success,
    callback_error=self._on_error
)
```

**API Parameters**: Use `max_completion_tokens` (not `max_tokens`). Temperature uses default (1).

## Technologies & Dependencies

### Backend (api/requirements.txt)
- **Flask** (>=3.0.0): Web framework
- **Flask-CORS** (>=3.0.10): Cross-origin resource sharing
- **Flasgger** (>=0.9.7): Swagger UI for API docs
- **TinyDB** (>=4.8.0): Lightweight NoSQL database
- **psutil** (>=5.9.0): Process management
- **OpenAI** (>=1.0.0): GPT-4o-mini integration
- **python-dotenv** (>=0.19.0): Env var management

### Frontend (frontend/package.json)
- **React** (18.2.0): Component-based UI
- **React Router** (6.20.0): Client-side routing
- **Axios** (1.6.2): HTTP client
- **Vite** (5.0.8): Build tool and dev server
- **TailwindCSS** (3.4.1): Utility-first CSS
- **DaisyUI** (4.6.0): Component library

### Standard Library
- `json`, `uuid`, `datetime`, `pathlib`, `typing`, `argparse`, `random`, `threading`, `signal`

**Minimum Python Version**: 3.7+

## Development Workflow

### Environment Setup
```powershell
# Virtual environment (CRITICAL — always use .venv)
python <script.py>

# Install all dependencies
npm run install:all
# Or separately:
pip install -r requirements.txt
cd frontend && npm install
```

### Running the Application

```bash
# Full stack (React + API) - RECOMMENDED
npm run dev

# API backend only
python api/main.py -i api         # Port 5000
python api/main.py -i api --debug  # With debug mode

# React frontend only
npm run dev:frontend                            # Port 3000

# Simulation mode (requires OPENAI_API_KEY)
python api/main.py -i simulation
```

**Access:**
- React UI: http://localhost:3000
- API Swagger: http://localhost:5000/api/docs
- API Root: http://localhost:5000 (auto-redirects to Swagger)

### Testing
```bash
python api/test.py          # Core functionality
python api/test_nosql.py    # NoSQL-specific
python api/test_api_key.py  # API key validation
```

### Deploying to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy (from project root)
vercel

# Production deploy
vercel --prod

# Set environment variables in Vercel dashboard:
# - OPENAI_API_KEY (for GPT features)
```

## Key Patterns & Conventions

### Import Pattern (CRITICAL)
All backend imports use **bare module names** (NOT `api.*` prefixed):
```python
# ✅ CORRECT (inside api/ code)
from core.models import World, Entity, Location
from storage import NoSQLStorage
from services import GPTService, CharacterService
from ai.gpt_client import GPTIntegration
from generators import WorldGenerator

# ❌ WRONG
from api.core.models import World
from api.storage import NoSQLStorage
```

### Story Linking Algorithm
Stories link when they share:
1. **Entities** (characters appearing in multiple stories)
2. **Locations** (same place, different stories)
3. **Time Cones** (temporal proximity)

Uses inverted indices: `{entity_id: [story_ids]}`.

### Auto-World Generation
Genre-to-world-type mapping (`api/generators/world_generator.py`):
- Adventure → Fantasy
- Mystery → Modern
- Conflict → Historical
- Discovery → Sci-Fi

### Database Schema (NoSQL)
Tables: `worlds`, `stories`, `locations`, `entities`, `time_cones`

```python
from tinydb import Query
WorldQuery = Query()
self.worlds.search(WorldQuery.world_id == world_id)
```

### Frontend API Pattern
All HTTP calls go through `frontend/src/services/api.js`:
```javascript
import { worldsAPI, storiesAPI, gptAPI } from '../services/api'
// Never use fetch/axios directly in components
```

## Critical Files for Understanding

### Backend (api/)
- `api/app.py`: Vercel serverless entrypoint (exposes `app` for WSGI)
- `api/main.py`: Local dev entrypoint (argument parsing, interface routing)
- `api/interfaces/api_backend.py`: Flask app setup, CORS, Swagger, blueprint registration
- `api/interfaces/routes/`: All API endpoint blueprints
- `api/services/gpt_service.py`: Async GPT service with callback pattern
- `api/services/character_service.py`: Character detection and formatting
- `api/generators/story_linker.py`: Core linking logic with graph algorithms
- `api/storage/nosql_storage.py`: Performance-critical storage layer (TinyDB)
- `api/core/models/world.py`: Base model pattern used by all domain objects
- `api/ai/gpt_client.py`: OpenAI GPT-4o-mini integration

### Frontend (frontend/)
- `frontend/src/services/api.js`: Centralized API client (Axios)
- `frontend/src/App.jsx`: Root component with React Router
- `frontend/src/pages/`: Route page components
- `frontend/src/containers/`: Data-fetching containers
- `frontend/src/components/`: Reusable UI components
- `frontend/vite.config.js`: Vite config with API proxy for dev

### Config
- `vercel.json`: Vercel monorepo deployment config
- `package.json`: Root npm scripts for local dev
- `.env`: Environment variables (OPENAI_API_KEY)

## Common Tasks

### Add New API Endpoint
1. Create or edit a blueprint in `api/interfaces/routes/`:
   ```python
   @bp.route('/api/your-endpoint', methods=['GET', 'POST'])
   def your_endpoint():
       return jsonify(result)
   ```
2. Register blueprint in `api/interfaces/routes/__init__.py` if new file
3. Add API call in `frontend/src/services/api.js`
4. Use in React components via the api service

### Add New World Type
1. Update `WORLD_TYPES` dict in `api/generators/world_generator.py`
2. Add themes, location_types, entity_types lists
3. Add option in React frontend dropdown component

### Add New Story Genre
1. Update `STORY_GENRES` in `api/generators/story_generator.py`
2. Add templates for that genre
3. Update genre dropdown in React frontend

### Add New Model Field
1. Update `__init__()` in model class (`api/core/models/`)
2. Add to `to_dict()` and `from_dict()`
3. Update storage backends if needed

### Debugging
- **API**: Enable debug mode with `--debug` flag, check Flask console output
- **Frontend**: Browser DevTools (F12) → Console + Network tabs
- **Storage**: Delete `.db` file to reset, check `get_stats()` for counts
- **Vercel**: Check Vercel dashboard logs, ensure env vars are set
- **CORS**: Check `api/interfaces/api_backend.py` allowed_origins list

## VS Code Configuration

**launch.json**: All configurations use `python` explicitly

**tasks.json**: Available tasks:
- `Run API Backend` — starts Flask API on port 5000
- `Run React Frontend` — starts Vite dev server on port 3000
- `Full Stack Dev` — runs both simultaneously
- `Run Tests` / `Run NoSQL Tests`
- `Build React` — production build
- `Install Backend Deps` / `Install Frontend Deps`
- `Clean DB Files`
- `Open Swagger Docs` / `Open React App`

**Python environment**: Virtual environment at `.venv/`

## Copilot Coding Guidelines

### Service Layer (Python — api/services/)
- All business logic must be in `api/services/` (never in Flask routes)
- Use callback pattern for async operations (see `GPTService`)
- Service methods should be stateless and reusable
- Never import Flask or UI code in services
- Use `to_dict()`/`from_dict()` for all model serialization
- Use `Service` suffix (e.g., `CharacterService`, `GPTService`)

### Frontend (React — frontend/src/)
- Use `services/api.js` for all HTTP requests (never call fetch/axios directly)
- UI logic in components; data logic in containers/hooks
- Use TailwindCSS utility classes and DaisyUI for styling
- Never use inline styles except for dynamic layout/animation
- Use React hooks and context for state management
- PascalCase for components, camelCase for functions/variables
- Extract repeated UI into reusable components with props

### General Rules
- **Never**: Mix business logic and UI, hardcode API URLs, duplicate code
- **Always**: Follow monorepo folder structure, use existing services/utilities
- **Imports**: Bare module names inside `api/` (no `api.*` prefix)
- **Paths**: Use `api/` prefix when referencing from project root (scripts, configs)

---
For more details, see `docs/` folder, `.github/skills/` folder, and this file.

## Skills Reference

Skills provide detailed patterns and best practices for specific domains. Located in `.github/skills/[name]/SKILL.md`:

| Skill | Path | Description |
|-------|------|-------------|
| `color` | `.github/skills/color/SKILL.md` | Color palette, DaisyUI theme, styling guidelines |
| `backend-api` | `.github/skills/backend-api/SKILL.md` | Flask routes, blueprints, auth, async GPT, error handling |
| `frontend-react` | `.github/skills/frontend-react/SKILL.md` | Container/View pattern, Heroicons, DaisyUI, GPT polling, code-splitting |
| `models-storage` | `.github/skills/models-storage/SKILL.md` | Domain models, TinyDB storage, serialization, permissions |
