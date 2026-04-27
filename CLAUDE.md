# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Interactive storytelling system with React frontend and Flask API backend, deployed as a Vercel monorepo. Features GPT-4o-mini integration for character simulation and content generation, MongoDB Atlas storage, and Facebook Graph API integration.

**Live**: https://story-creator-cyan.vercel.app

## Development Commands

### Full Stack Development

```bash
# Start both frontend and backend (RECOMMENDED)
npm run dev

# Backend only (Flask API on port 5000)
python api/main.py -i api

# Backend with debug mode
python api/main.py -i api --debug

# Frontend only (Next.js on port 3000)
npm run dev:frontend

# Simulation mode (requires OPENAI_API_KEY)
python api/main.py -i simulation
```

**Access URLs**:
- React UI: http://localhost:3000
- API Swagger: http://localhost:5000/api/docs

### Installation

```bash
# Install all dependencies (backend + frontend)
npm run install:all

# Or separately:
npm run install:backend    # pip install -r requirements.txt
# npm install              # frontend (Next.js) deps
```

### Testing

```bash
# NoSQL storage tests
python api/test_nosql.py

# API key validation tests
python api/test_api_key.py

# API integration tests
python api/test_api.py

# Permission system tests
python api/test_permissions.py
```

### Building & Deployment

```bash
# Build frontend
npm run build

# Deploy to Vercel (from project root)
vercel

# Production deploy
vercel --prod
```

## Architecture

### Monorepo Structure

```
story-creator/
├── api/                          # Python Flask backend
│   ├── app.py                    # Vercel serverless entrypoint
│   ├── main.py                   # Local development entrypoint
│   ├── ai/                       # GPT-4o-mini integration
│   ├── core/
│   │   ├── models/               # Domain models (World, Story, Entity, Location)
│   │   ├── exceptions.py         # Custom exception hierarchy (APIException subclasses)
│   │   └── permissions.py        # Role/permission definitions
│   ├── generators/               # Content generators and story linker
│   ├── interfaces/               # Flask app, routes, middleware
│   │   ├── api_backend.py        # Flask app factory + route registration
│   │   ├── auth_middleware.py    # @token_required, @admin_required decorators
│   │   ├── error_handlers.py     # Global exception → JSON response mapping
│   │   └── routes/               # Blueprint files (world, story, auth, gpt, etc.)
│   ├── schemas/                  # Marshmallow validation schemas
│   ├── services/                 # Business logic layer (CRITICAL)
│   ├── storage/                  # MongoDB Atlas storage (MongoStorage + BaseStorage)
│   ├── utils/
│   │   ├── responses.py          # success_response, created_response, paginated_response
│   │   └── validation.py         # @validate_request, @validate_query_params decorators
│   └── visualization/            # Relationship diagrams
│
├── app/                          # Next.js app router (pages, layouts)
├── src/                          # React components and client code
│   ├── components/               # Reusable UI components
│   ├── containers/               # Data-fetching containers
│   ├── contexts/                 # AuthContext, GptTaskContext
│   ├── hooks/                    # useKeepAlive and other custom hooks
│   ├── services/api.js           # Centralized Axios API client
│   └── views/                    # Page-level view components
│
├── requirements.txt              # Python dependencies
├── vercel.json                   # Vercel deployment config
├── package.json                  # Root npm scripts + Next.js frontend
└── .env                          # OPENAI_API_KEY, GOOGLE_*, FACEBOOK_*
```

### Critical Import Pattern (MUST FOLLOW)

**All backend imports use bare module names** (NOT `api.*` prefixed):

```python
# ✅ CORRECT (inside api/ code)
from core.models import World, Entity, Story, Location
from storage import MongoStorage
from services import GPTService, CharacterService, AuthService
from ai.gpt_client import GPTIntegration
from generators import WorldGenerator, StoryLinker

# ❌ WRONG - DO NOT USE
from api.core.models import World
from api.storage import NoSQLStorage
```

**Why**: Both `api/app.py` (Vercel) and `api/main.py` (local) add `api/` directory to `sys.path`, making bare imports work correctly.

### Service Layer Architecture

**Business logic MUST be in `api/services/`** - never in Flask routes:

- **GPTService** (`gpt_service.py`): Async GPT operations with callbacks
- **CharacterService** (`character_service.py`): Character detection and management
- **AuthService** (`auth_service.py`): JWT authentication with Google/Facebook OAuth
- **FacebookService** (`facebook_service.py`): Facebook Graph API integration
- **EventService** (`event_service.py`): Event and timeline management
- **PermissionService** (`permission_service.py`): Authorization and permissions

**Pattern**: Services use callback pattern for async operations. Routes delegate all logic to services.

### Storage Layer

**Primary**: MongoDB Atlas via `MongoStorage` class (`api/storage/mongo_storage.py`)
- Requires `MONGODB_URI` environment variable
- Local dev fallback: `mongomock` (in-memory) when `MONGODB_URI` not set
- Lazy connection: thread-safe singleton, defers connection to first operation
- Auto-creates indexes on `story_id`, `world_id`, `visibility`, `owner_id`, `shared_with`
- Collections: `worlds`, `stories`, `locations`, `entities`, `time_cones`, `events`, `event_analysis_cache`, `users`, `gpt_tasks`
- Save pattern: `stories.replace_one({'story_id': id}, data, upsert=True)` (atomic upsert)
- MongoDB `_id` field stripped before returning to API via `_clean_doc()`

**Abstraction**: `BaseStorage` (`api/storage/base_storage.py`) — abstract interface allowing storage backend swaps

### Frontend API Client

**All HTTP calls MUST go through** `src/services/api.js`:

```javascript
import { worldsAPI, storiesAPI, gptAPI, authAPI } from '../services/api'
// Never use fetch or axios directly in components
```

API base URL:
- Development: `http://localhost:5000/api` (via Next.js rewrites / proxy)
- Production: `/api` (Vercel rewrites to `api/app.py`)

### Authentication

JWT-based authentication with:
- Google OAuth (via `@react-oauth/google`)
- Facebook OAuth (via `@greatsumini/react-facebook-login`)
- Session management in `AuthContext`
- Protected routes via `auth_middleware.py`
- Role-based permissions: `admin`, `editor`, `viewer`

### Vercel Deployment

**Config** (`vercel.json`):
- Build: `npm run build` (Next.js)
- Rewrites: `/api/*` → `api/app.py` (serverless function)
- Next.js handles all other routing

**Environment Variables** (set in Vercel dashboard):
- `OPENAI_API_KEY` - for GPT features
- `GOOGLE_CLIENT_ID` - for Google OAuth
- `FACEBOOK_APP_ID` - for Facebook OAuth
- `JWT_SECRET` - for token signing
- `MONGODB_URI` - for MongoDB Atlas (required for persistent storage; falls back to mongomock in dev)

## Key Technologies

### Backend
- **Flask** 3.0+ - Web framework
- **MongoDB Atlas** + **pymongo** - Primary database
- **mongomock** - In-memory MongoDB for local dev (no URI needed)
- **OpenAI** 1.0+ - GPT-4o-mini integration
- **PyJWT** 2.8+ - JWT authentication
- **Marshmallow** 3.20+ - Request validation schemas
- **Authlib** 1.3+ - OAuth support
- **Flasgger** 0.9+ - Swagger UI

### Frontend
- **Next.js** 14 - Framework + build tool
- **React** 18.2 - UI framework
- **TailwindCSS** 3.4 + **DaisyUI** 4.6 - Styling
- **Axios** 1.6 - HTTP client
- **@xyflow/react** 12.10 - Timeline visualization

## Important Patterns

### Error Handling (MUST FOLLOW)

**Never** return manual `jsonify({'error': ...})` from routes. Always raise typed exceptions from `core.exceptions`:

```python
from core.exceptions import (
    ResourceNotFoundError,   # 404 — resource_not_found
    PermissionDeniedError,   # 403 — permission_denied
    ValidationError,         # 400 — validation_error
    QuotaExceededError,      # 429 — quota_exceeded
    AuthenticationError,     # 401 — authentication_error
    ConflictError,           # 409 — conflict
    BusinessRuleError,       # 400 — business_rule_violation
    ExternalServiceError     # 502 — external_service_error
)

# ✅ CORRECT
if not world_data:
    raise ResourceNotFoundError('World', world_id)
if not PermissionService.can_edit(user_id, world_data):
    raise PermissionDeniedError('edit', 'world')

# ❌ WRONG
if not world_data:
    return jsonify({'error': 'World not found'}), 404
```

### Standardized Response Utilities (MUST FOLLOW)

```python
from utils.responses import (
    success_response,    # 200 — generic success
    created_response,    # 201 — after creating a resource
    deleted_response,    # 200 — after deleting a resource
    paginated_response,  # 200 — for list endpoints
    accepted_response,   # 202 — for async/background tasks
)

# ✅ CORRECT
return success_response(world_data)
return created_response(world.to_dict(), "World created successfully")
return deleted_response("World deleted successfully")
return paginated_response(items, page, per_page, total)

# ❌ WRONG
return jsonify(world_data)
return jsonify({'message': 'Deleted'}), 200
```

### Request Validation (MUST FOLLOW for POST/PUT endpoints)

```python
from utils.validation import validate_request, validate_query_params
from schemas.world_schemas import CreateWorldSchema, ListWorldsQuerySchema

@world_bp.route('/api/worlds', methods=['POST'])
@token_required
@validate_request(CreateWorldSchema)
def create_world():
    data = request.validated_data  # pre-validated dict

@world_bp.route('/api/worlds', methods=['GET'])
@optional_auth
@validate_query_params(ListWorldsQuerySchema)
def list_worlds():
    params = request.validated_data
```

Schemas live in `api/schemas/`. Use Marshmallow.

### Domain Models

All models in `api/core/models/` follow this pattern:
- `__init__()` for initialization
- `to_dict()` / `from_dict()` for serialization
- `to_json()` / `from_json()` for JSON strings
- Models: `World`, `Story`, `Entity`, `Location`, `TimeCone`, `Event`, `User`

### Story Linking Algorithm

Stories automatically link when sharing:
1. **Entities** - characters appearing in multiple stories
2. **Locations** - same place, different stories
3. **Time Cones** - temporal proximity

Uses inverted indices: `{entity_id: [story_ids]}` for efficient graph building.

### GPT Integration

Model: `gpt-4o-mini`
- Use `max_completion_tokens` parameter (not `max_tokens`)
- Temperature defaults to 1
- Async operations via `GPTService` with callbacks
- Auto-translation ENG→VN in simulation mode

### VS Code Integration

Tasks available in `.vscode/tasks.json`:
- `Run API Backend` - Flask API
- `Run React Frontend` - Next.js dev server
- `Full Stack Dev` - Both simultaneously
- `Run Tests` - Test suites
- `Build React` - Production build

## Environment Setup

```bash
# Create virtual environment (if not exists)
python -m venv .venv

# Activate
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\Activate.ps1    # Windows PowerShell

# Install dependencies
npm run install:all

# Configure environment variables
# Create .env file with:
OPENAI_API_KEY=sk-your-key-here
GOOGLE_CLIENT_ID=your-google-client-id
FACEBOOK_APP_ID=your-facebook-app-id
JWT_SECRET=your-secret-key
```

## Additional Documentation

For more detailed information, see:
- `.github/copilot-instructions.md` - Comprehensive architecture and patterns
- `README.md` - Quick start and feature overview
- `docs/` - Detailed guides and API documentation
