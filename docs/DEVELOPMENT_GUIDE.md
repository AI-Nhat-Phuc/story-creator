# Development Guide - Story Creator

## Getting Started

### Prerequisites

- **Python**: 3.9+
- **Node.js**: 18+
- **Git**
- **VS Code** (recommended)

### Initial Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd story-creator

# 2. Install all dependencies
npm run install:all

# 3. Create .env file
cp .env.example .env
# Edit .env and set OPENAI_API_KEY, GOOGLE_CLIENT_ID, JWT_SECRET, etc.

# 4. Start full stack (recommended)
npm run dev

# 5. Verify setup
python api/test_nosql.py
```

---

## Project Structure

```
story-creator/
├── api/                              # Python Flask backend
│   ├── app.py                        # Vercel serverless entrypoint
│   ├── main.py                       # Local development entrypoint
│
│   │
│   ├── ai/                           # GPT-4o-mini integration
│   │   ├── gpt_client.py            # OpenAI API wrapper
│   │   └── prompts.py               # Prompt templates
│   │
│   ├── core/                         # Domain layer
│   │   ├── models/                   # World, Story, Entity, Location, User
│   │   ├── exceptions.py             # Custom exception hierarchy
│   │   └── permissions.py           # Role & permission definitions
│   │
│   ├── generators/                   # Content generators
│   │   ├── world_generator.py
│   │   ├── story_generator.py
│   │   └── story_linker.py
│   │
│   ├── interfaces/                   # HTTP layer
│   │   ├── api_backend.py           # Flask app factory
│   │   ├── auth_middleware.py        # JWT decorators
│   │   ├── error_handlers.py         # Global exception → JSON handlers
│   │   └── routes/                   # Blueprint route files
│   │       ├── world_routes.py
│   │       ├── story_routes.py
│   │       ├── auth_routes.py
│   │       ├── gpt_routes.py
│   │       ├── event_routes.py
│   │       ├── facebook_routes.py
│   │       ├── admin_routes.py
│   │       ├── stats_routes.py
│   │       └── health_routes.py
│   │
│   ├── schemas/                      # Marshmallow validation schemas
│   │   ├── world_schemas.py
│   │   ├── story_schemas.py
│   │   └── auth_schemas.py
│   │
│   ├── services/                     # Business logic layer
│   │   ├── auth_service.py
│   │   ├── gpt_service.py
│   │   ├── character_service.py
│   │   ├── permission_service.py
│   │   ├── event_service.py
│   │   └── facebook_service.py
│   │
│   ├── storage/                      # Persistence layer
│   │   ├── nosql_storage.py         # TinyDB (default)
│   │   └── mongo_storage.py         # MongoDB (optional)
│   │
│   └── utils/                        # Shared utilities
│       ├── responses.py              # Standardized response helpers
│       └── validation.py            # @validate_request decorator
│
├── app/                              # Next.js app router (pages, layouts)
├── src/                              # React components and client code
│   ├── components/                  # Reusable UI components
│   ├── containers/                  # Data-fetching containers
│   ├── contexts/                    # AuthContext, GptTaskContext
│   ├── hooks/                       # Custom hooks
│   ├── services/api.js              # Centralized Axios client
│   └── views/                       # Page-level view components
│
├── requirements.txt                  # Python dependencies
├── vercel.json                       # Vercel deployment config
├── package.json                      # Root npm scripts + Next.js frontend
├── CLAUDE.md                         # Claude Code instructions
└── .env                              # OPENAI_API_KEY, JWT_SECRET, etc.
```

---

## Development Commands

```bash
# Full stack (recommended)
npm run dev

# Backend only
python api/main.py -i api

# Frontend only
npm run dev:frontend

# Tests
python api/test_nosql.py
python api/test_api.py

# Build for production
npm run build
```

**URLs:**
- React UI: http://localhost:3000
- API Swagger: http://localhost:5000/api/docs

---

## Backend Architecture Patterns

### Import Convention

All backend imports use **bare module names** (never `api.*` prefixed):

```python
# ✅ Correct
from core.models import World, Entity, Story
from core.exceptions import ResourceNotFoundError, PermissionDeniedError
from services import CharacterService, PermissionService
from utils.responses import success_response, created_response
from utils.validation import validate_request
from schemas.world_schemas import CreateWorldSchema

# ❌ Wrong
from api.core.models import World
from api.utils.responses import success_response
```

### Exception-Based Error Handling

Never return manual error `jsonify()` from routes. Always raise typed exceptions:

```python
from core.exceptions import (
    ResourceNotFoundError,    # 404
    PermissionDeniedError,    # 403
    ValidationError,          # 400
    QuotaExceededError,       # 429
    AuthenticationError,      # 401
    ConflictError,            # 409
    BusinessRuleError,        # 400
    ExternalServiceError      # 502
)

# ✅ Correct
world = storage.load_world(world_id)
if not world:
    raise ResourceNotFoundError('World', world_id)

# ❌ Wrong (old pattern)
if not world:
    return jsonify({'error': 'World not found'}), 404
```

### Standardized Responses

```python
from utils.responses import (
    success_response,    # 200 { success, data, message? }
    created_response,    # 201 { success, data, message }
    deleted_response,    # 200 { success, data: null, message }
    paginated_response,  # 200 { success, data: [], pagination: {...} }
    accepted_response,   # 202 for async operations
)

# ✅ Correct
return success_response(world_data)
return created_response(world.to_dict(), "World created successfully")
return paginated_response(items, page, per_page, total)
return deleted_response("World deleted successfully")

# ❌ Wrong (old pattern)
return jsonify(world_data)
return jsonify({'message': 'World deleted'}), 200
```

### Request Validation

```python
from utils.validation import validate_request, validate_query_params
from schemas.world_schemas import CreateWorldSchema, ListWorldsQuerySchema

@world_bp.route('/api/worlds', methods=['POST'])
@token_required
@validate_request(CreateWorldSchema)          # validates request.json
def create_world():
    data = request.validated_data             # already validated dict
    ...

@world_bp.route('/api/worlds', methods=['GET'])
@optional_auth
@validate_query_params(ListWorldsQuerySchema) # validates request.args
def list_worlds():
    params = request.validated_data
    page = params.get('page', 1)
    ...
```

### Adding a New Route

Follow this pattern for any new endpoint:

```python
# 1. Define schema in api/schemas/
class CreateFooSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    type = fields.Str(validate=validate.OneOf(['a', 'b']), load_default='a')

# 2. Write the route in api/interfaces/routes/
@foo_bp.route('/api/foos', methods=['POST'])
@token_required
@validate_request(CreateFooSchema)
def create_foo():
    data = request.validated_data

    existing = storage.load_foo(data['name'])
    if existing:
        raise ConflictError(f"Foo '{data['name']}' already exists")

    foo = Foo(name=data['name'], foo_type=data['type'])
    foo.owner_id = g.current_user.user_id
    storage.save_foo(foo.to_dict())

    return created_response(foo.to_dict(), "Foo created successfully")
```

### Adding a Validation Schema

```python
# api/schemas/foo_schemas.py
from marshmallow import Schema, fields, validate

class CreateFooSchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'Name is required'}
    )
    category = fields.Str(
        validate=validate.OneOf(['alpha', 'beta']),
        load_default='alpha'
    )

class ListFooQuerySchema(Schema):
    page = fields.Int(validate=validate.Range(min=1), load_default=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), load_default=20)
```

---

## Frontend Patterns

### API Calls

All HTTP calls go through `src/services/api.js`. Never use `fetch` or `axios` directly in components:

```javascript
// ✅ Correct
import { worldsAPI, storiesAPI } from '../services/api'

const response = await worldsAPI.getAll()
const worlds = response.data.data        // paginated: response.data.data
const total = response.data.pagination.total

const detail = await worldsAPI.getById(id)
const world = detail.data.data           // success: response.data.data

// ❌ Wrong
const response = await fetch('/api/worlds')
```

### Error Handling in Frontend

```javascript
try {
  const response = await worldsAPI.create(formData)
  const world = response.data.data
  // success
} catch (error) {
  const errorData = error.response?.data?.error
  const message = errorData?.message || 'Unknown error'
  const code = errorData?.code         // 'validation_error', 'quota_exceeded', etc.
  const details = errorData?.details   // field-level validation errors
}
```

---

## Testing

```bash
# Core unit tests
python api/test_nosql.py

# Storage tests
python api/test_nosql.py

# API key validation
python api/test_api_key.py

# API integration tests
python api/test_api.py

# Permission system
python api/test_permissions.py
```

### Manual Testing Checklist

- [ ] Register / login / verify token
- [ ] Create world (with/without GPT)
- [ ] Create story with selected characters
- [ ] GPT analyze + batch analyze
- [ ] Events timeline extraction
- [ ] World share/unshare
- [ ] Admin: change role, ban user, toggle Facebook access
- [ ] Error cases return correct `error.code`

---

## Coding Standards

### Python

- Follow **PEP 8**
- Use **snake_case** for variables/functions, **PascalCase** for classes
- Use **type hints** on public methods
- Use **exceptions** over manual error returns (see patterns above)

### Import Order

```python
# 1. Standard library
import uuid
import threading

# 2. Third-party
from flask import Blueprint, request, g
from marshmallow import Schema, fields

# 3. Local (bare module names)
from core.exceptions import ResourceNotFoundError
from utils.responses import success_response
from schemas.world_schemas import CreateWorldSchema
```

---

## Deployment

### Vercel

```bash
# Preview deploy
vercel

# Production deploy
vercel --prod
```

**Required environment variables** (set in Vercel dashboard):
- `OPENAI_API_KEY`
- `GOOGLE_CLIENT_ID`
- `FACEBOOK_APP_ID`
- `JWT_SECRET`
- `MONGODB_URI` (optional, for persistent storage)

### Local Production

```bash
pip install waitress
waitress-serve --host=127.0.0.1 --port=5000 --call 'interfaces.api_backend:create_app'
```

---

## Debugging

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Activate venv: `source .venv/Scripts/activate` |
| Port 5000 in use | Kill process or use `--port 8080` |
| DB locked | Restart server; delete `story_creator.db` if corrupt |
| GPT 502 error | Check `OPENAI_API_KEY` in `.env` |
| JWT decode fails | Check `JWT_SECRET` matches between requests |

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Loading world: {world_id}")
logger.info("World created successfully")
logger.warning("GPT not available, using fallback")
logger.error(f"Storage error: {e}")
```

---

## Security Checklist

- [x] JWT authentication on all protected routes
- [x] Role-based access control (admin/moderator/user/guest)
- [x] Input validation via Marshmallow schemas
- [x] Centralized error handling (no stack traces leaked)
- [x] Password hashing (never stored plain)
- [ ] Rate limiting (planned — Phase 4)
- [ ] HTTPS (enforced by Vercel in production)
- [ ] Keep dependencies updated

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)
- [TinyDB Documentation](https://tinydb.readthedocs.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [React Documentation](https://react.dev/)
- [TailwindCSS + DaisyUI](https://daisyui.com/components/)
- [Vite Documentation](https://vitejs.dev/)
