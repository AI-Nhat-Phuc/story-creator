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
