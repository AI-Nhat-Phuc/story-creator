---
name: backend-api
description: Backend API development patterns for Flask routes, blueprints, auth decorators, async GPT tasks, and error handling. Use when creating or editing API endpoints in api/interfaces/routes/.
---

# Skill: Backend API Development

## When to Apply
When creating or editing API endpoints in `api/interfaces/routes/`.

## Pattern: Creating a New API Endpoint

### 1. Route Blueprint

```python
# api/interfaces/routes/my_routes.py
from flask import Blueprint, request, jsonify, g
from interfaces.auth_middleware import token_required, optional_auth, admin_required

def create_my_bp(storage, flush_data, **kwargs):
    """Create blueprint. Receive dependencies via parameters, do NOT use globals."""
    my_bp = Blueprint('my_feature', __name__)

    @my_bp.route('/api/my-resource', methods=['GET'])
    @optional_auth  # or @token_required if login is required
    def list_resources():
        """Swagger docstring.
        ---
        tags:
          - MyFeature
        parameters:
          - name: param1
            in: query
            type: string
        responses:
          200:
            description: Success
        """
        user_id = g.current_user.user_id if hasattr(g, 'current_user') else None
        # Business logic...
        return jsonify(result)

    return my_bp
```

### 2. Register Blueprint

```python
# api/interfaces/routes/__init__.py
from .my_routes import create_my_bp

# api/interfaces/api_backend.py → _register_blueprints()
my_bp = create_my_bp(storage=self.storage, flush_data=self._flush_data)
self.app.register_blueprint(my_bp)
```

### 3. Frontend API Client

```javascript
// frontend/src/services/api.js
export const myAPI = {
  getAll: () => api.get('/my-resource'),
  getById: (id) => api.get(`/my-resource/${id}`),
  create: (data) => api.post('/my-resource', data),
}
```

## Best Practices

### Import Pattern (REQUIRED)
```python
# ✅ CORRECT — bare module names (inside api/)
from core.models import World, Story, Entity, Location
from storage import NoSQLStorage
from services import GPTService
from generators import StoryLinker

# ❌ WRONG — do not use api.* prefix
from api.core.models import World
```

### Auth Decorators
| Decorator | When to use |
|-----------|-------------|
| `@token_required` | Routes that require login (POST, PUT, DELETE) |
| `@optional_auth` | Routes that work with or without login (public GET but need user context) |
| `@admin_required` | Routes restricted to admin only |

```python
# Safe user_id retrieval (use with @optional_auth)
user_id = g.current_user.user_id if hasattr(g, 'current_user') else None

# Required user_id (use with @token_required)
user_id = g.current_user.user_id
```

### Async GPT Tasks
Pattern for long-running operations (GPT calls):

```python
task_id = str(uuid.uuid4())
gpt_results[task_id] = {'status': 'pending'}

def background_work():
    try:
        # ... processing ...
        gpt_results[task_id] = {'status': 'completed', 'result': data}
    except Exception as e:
        gpt_results[task_id] = {'status': 'error', 'result': str(e)}

thread = threading.Thread(target=background_work, daemon=True)
thread.start()
return jsonify({'task_id': task_id})
```

Frontend polling:
```javascript
const pollResults = async (taskId) => {
  const result = await gptAPI.getResults(taskId)
  if (result.data.status === 'completed') {
    // Done
  } else if (result.data.status === 'error') {
    // Error
  } else {
    setTimeout(() => pollResults(taskId), 1000)
  }
}
```

### Flush Data
Always call `flush_data()` after modifying storage:
```python
storage.save_story(story_data)
flush_data()
```

### Error Responses
```python
return jsonify({'error': 'Message'}), 400   # Validation error
return jsonify({'error': 'Not found'}), 404  # Resource not found
return jsonify({'error': 'GPT not available'}), 503  # Service unavailable
```

### Limits & Validation
```python
MAX_BATCH = 3
if len(items) > MAX_BATCH:
    return jsonify({'error': f'Maximum {MAX_BATCH} items per request'}), 400
```

## Anti-patterns

- ❌ Business logic in route handler → move to `services/`
- ❌ Import Flask objects directly in service layer
- ❌ Hardcode API keys or secrets
- ❌ Synchronous GPT calls in request handler → use threading
- ❌ Forget `flush_data()` after save
- ❌ Forget `@optional_auth` for GET routes that need visibility filtering

---

## Python Project Structure Best Practices

> Reference: https://docs.python-guide.org/writing/structure/

### Repository Layout

```
api/                      # Python package root (added to sys.path)
├── app.py                # Vercel serverless entrypoint
├── main.py               # Local dev entrypoint
├── core/
│   └── models/           # Domain model classes
├── generators/           # Content generation logic
├── interfaces/           # Flask app + blueprints (I/O layer)
│   ├── api_backend.py
│   └── routes/           # One file per resource/feature
├── services/             # Business logic layer (stateless)
├── storage/              # Persistence layer
└── ai/                   # External API integration
```

Key rule: **one responsibility per module**. Route files handle HTTP; service files handle business logic; model files define data.

### Modules & Packages

- Each `__init__.py` exposes a clean public API for the package:
  ```python
  # services/__init__.py
  from .gpt_service import GPTService
  from .batch_analyze_service import BatchAnalyzeService
  __all__ = ['GPTService', 'BatchAnalyzeService']
  ```
- Import only what is needed — avoid `from module import *`
- Use absolute imports within `api/` (bare module names, not relative `.`)

### Separation of Concerns

| Layer | Responsibility | Location |
|-------|---------------|----------|
| Routes | HTTP in/out, request parsing, auth decorators | `interfaces/routes/` |
| Services | Business logic, orchestration | `services/` |
| Models | Data structure, serialization | `core/models/` |
| Storage | Persistence (read/write) | `storage/` |
| AI | External GPT calls | `ai/` |

Never mix layers. A route handler should call a service; the service calls storage and models.

### When to Split a File

Split a module when it meets any of these criteria:
- **> 300 lines** and contains multiple distinct concerns
- Contains business logic inside a route handler → move to `services/`
- Logic is reused across multiple places → create a dedicated helper/service
- Logic can be unit tested in isolation → signal to extract a service

Example: batch-analyze logic from `gpt_routes.py` was extracted to `services/batch_analyze_service.py`.

### Avoiding Circular Imports

- `routes/` can import from `services/`, `core/models/`, `storage/`
- `services/` can import from `core/models/`, `storage/`, `ai/`
- `core/models/` must NOT import from `services/` or `routes/`
- `storage/` must NOT import from `services/` or `routes/`

### Testing

Each layer should have its own test file:
- `test.py` — core models, generators, JSON storage
- `test_nosql.py` — NoSQL storage CRUD and performance
- `test_api.py` — Flask API endpoints (using `app.test_client()`)

Run tests:
```bash
python api/test.py
python api/test_nosql.py
python api/test_api.py
```

Creating tests for a new API endpoint:
```python
# Initialize backend with a temp database
backend = APIBackend(db_path=temp_db_path)
with backend.app.test_client() as client:
    resp = client.get('/api/health')
    assert resp.status_code == 200
```

