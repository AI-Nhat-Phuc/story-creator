---
name: backend-api
description: Backend API development patterns for Flask routes, blueprints, auth decorators, async GPT tasks, and error handling. Use when creating or editing API endpoints in api/interfaces/routes/.
---

# Skill: Backend API Development

## Khi nào áp dụng
Khi tạo hoặc chỉnh sửa API endpoint trong `api/interfaces/routes/`.

## Pattern: Tạo mới API Endpoint

### 1. Route Blueprint

```python
# api/interfaces/routes/my_routes.py
from flask import Blueprint, request, jsonify, g
from interfaces.auth_middleware import token_required, optional_auth, admin_required

def create_my_bp(storage, flush_data, **kwargs):
    """Create blueprint. Nhận dependencies qua parameter, KHÔNG import global."""
    my_bp = Blueprint('my_feature', __name__)

    @my_bp.route('/api/my-resource', methods=['GET'])
    @optional_auth  # hoặc @token_required nếu bắt buộc login
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

### 2. Đăng ký Blueprint

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

### Import Pattern (BẮT BUỘC)
```python
# ✅ ĐÚNG — bare module names (bên trong api/)
from core.models import World, Story, Entity, Location
from storage import NoSQLStorage
from services import GPTService
from generators import StoryLinker

# ❌ SAI — không dùng api.* prefix
from api.core.models import World
```

### Auth Decorators
| Decorator | Khi nào dùng |
|-----------|-------------|
| `@token_required` | Route yêu cầu đăng nhập (POST, PUT, DELETE) |
| `@optional_auth` | Route hoạt động cả login/không login (GET công khai nhưng cần user context) |
| `@admin_required` | Route chỉ dành cho admin |

```python
# Lấy user_id an toàn (dùng với @optional_auth)
user_id = g.current_user.user_id if hasattr(g, 'current_user') else None

# Lấy user_id bắt buộc (dùng với @token_required)
user_id = g.current_user.user_id
```

### Async GPT Tasks
Pattern cho các operation chạy lâu (GPT calls):

```python
task_id = str(uuid.uuid4())
gpt_results[task_id] = {'status': 'pending'}

def background_work():
    try:
        # ... xử lý ...
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
Luôn gọi `flush_data()` sau khi thay đổi storage:
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

### Giới hạn & Validation
```python
MAX_BATCH = 3
if len(items) > MAX_BATCH:
    return jsonify({'error': f'Tối đa {MAX_BATCH} items mỗi lần'}), 400
```

## Anti-patterns (TRÁNH)

- ❌ Business logic trong route handler → chuyển vào `services/`
- ❌ Import trực tiếp Flask object trong service layer
- ❌ Hardcode API key hoặc secrets
- ❌ Gọi GPT đồng bộ trong request handler (dùng threading)
- ❌ Quên `flush_data()` sau khi save
- ❌ Quên `@optional_auth` cho route GET cần filter theo visibility

---

## Python Project Structure Best Practices

> Reference: https://docs.python-guide.org/writing/structure/

### Cấu trúc thư mục (Repository Layout)

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

### Khi nào tách file mới?

Tách module khi một file đáp ứng bất kỳ tiêu chí nào sau:
- **> 300 dòng** và chứa nhiều khái niệm khác nhau
- Chứa business logic bên trong route handler → chuyển sang `services/`
- Logic được dùng lại ở nhiều nơi → tạo helper/service riêng
- Logic có thể unit test độc lập → dấu hiệu nên tách service

Ví dụ đã áp dụng: logic batch-analyze từ `gpt_routes.py` được tách thành `services/batch_analyze_service.py`.

### Tránh Circular Imports

- `routes/` có thể import từ `services/`, `core/models/`, `storage/`
- `services/` có thể import từ `core/models/`, `storage/`, `ai/`
- `core/models/` KHÔNG import từ `services/` hoặc `routes/`
- `storage/` KHÔNG import từ `services/` hoặc `routes/`

### Testing

Mỗi layer nên có test file riêng:
- `test.py` — core models, generators, JSON storage
- `test_nosql.py` — NoSQL storage CRUD và performance
- `test_api.py` — Flask API endpoints (sử dụng `app.test_client()`)

Chạy test:
```bash
python api/test.py
python api/test_nosql.py
python api/test_api.py
```

Tạo test cho API endpoint mới:
```python
# Khởi tạo backend với temp database
backend = APIBackend(db_path=temp_db_path)
with backend.app.test_client() as client:
    resp = client.get('/api/health')
    assert resp.status_code == 200
```

