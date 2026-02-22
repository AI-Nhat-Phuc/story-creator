---
name: models-storage
description: Domain model and storage patterns for TinyDB/NoSQL, model serialization (to_dict/from_dict), visibility/permissions, and database operations. Use when creating or editing models in api/core/models/ or storage code.
---

# Skill: Domain Models & Storage

## Khi nào áp dụng
Khi tạo hoặc chỉnh sửa domain models trong `api/core/models/` hoặc storage operations.

## Pattern: Domain Model

### Tạo Model Mới

```python
# api/core/models/my_model.py
"""MyModel model description."""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class MyModel:
    """Represents a my_model entity."""

    def __init__(
        self,
        name: str,
        world_id: str,
        my_model_id: Optional[str] = None,
        created_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        visibility: str = 'private',
        owner_id: Optional[str] = None,
        shared_with: Optional[List[str]] = None
    ):
        self.my_model_id = my_model_id or str(uuid.uuid4())
        self.name = name
        self.world_id = world_id
        self.created_at = created_at or datetime.now().isoformat()
        self.metadata = metadata or {}
        self.visibility = visibility
        self.owner_id = owner_id
        self.shared_with = shared_with or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'my_model_id': self.my_model_id,
            'name': self.name,
            'world_id': self.world_id,
            'created_at': self.created_at,
            'metadata': self.metadata,
            'visibility': self.visibility,
            'owner_id': self.owner_id,
            'shared_with': self.shared_with,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MyModel':
        """Create from dictionary."""
        instance = cls(
            name=data.get('name', ''),
            world_id=data.get('world_id', ''),
            my_model_id=data.get('my_model_id'),
            created_at=data.get('created_at'),
            metadata=data.get('metadata'),
            visibility=data.get('visibility', 'private'),
            owner_id=data.get('owner_id'),
            shared_with=data.get('shared_with'),
        )
        return instance

    @classmethod
    def from_json(cls, json_str: str) -> 'MyModel':
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))
```

### Đăng ký Model

```python
# api/core/models/__init__.py
from .my_model import MyModel
```

## Existing Models

| Model | ID Field | Thuộc World | Key Fields |
|-------|----------|-------------|------------|
| `World` | `world_id` | — | `name`, `world_type`, `description`, `entities[]`, `locations[]`, `stories[]` |
| `Story` | `story_id` | `world_id` | `title`, `content`, `entities[]`, `locations[]`, `linked_stories[]`, `time_cones[]` |
| `Entity` | `entity_id` | `world_id` | `name`, `entity_type`, `description`, `attributes{}` |
| `Location` | `location_id` | `world_id` | `name`, `description`, `coordinates{x,y}` |
| `TimeCone` | `time_cone_id` | — | `time_index`, `story_id`, `world_id` |
| `Event` | `event_id` | `world_id` | `title`, `description`, `story_id`, `characters[]`, `locations[]` |
| `User` | `user_id` | — | `username`, `email`, `password_hash`, `role` |

## Storage Layer

### NoSQLStorage (TinyDB — mặc định)

```python
from storage import NoSQLStorage
from tinydb import Query

storage = NoSQLStorage('story_creator.db')

# CRUD
storage.save_world(world_dict)
storage.load_world(world_id)        # → dict hoặc None
storage.list_worlds()               # → List[dict]
storage.delete_world(world_id)

# Với user context (filter visibility)
storage.list_stories(world_id, user_id=user_id)
storage.list_worlds(user_id=user_id)

# Entity/Location
storage.save_entity(entity_dict)
storage.list_entities(world_id)
storage.save_location(loc_dict)
storage.list_locations(world_id)

# Flush (BẮT BUỘC sau khi write)
storage.flush()
```

### Vercel Deployment
- Database path: `/tmp/story_creator.db` (read-only filesystem)
- Data KHÔNG persist giữa các invocations
- Set qua env var `STORY_DB_PATH`

## Visibility & Permissions

```python
# Visibility levels
'public'   # Ai cũng xem được
'private'  # Chỉ owner
'shared'   # Owner + shared_with list

# Permission check
from services import PermissionService
can_view = PermissionService.can_view(resource, user_id)
can_edit = PermissionService.can_edit(resource, user_id)
can_delete = PermissionService.can_delete(resource, user_id)
```

## Anti-patterns (TRÁNH)

- ❌ Thêm field mà quên cập nhật `to_dict()` và `from_dict()`
- ❌ Dùng storage trực tiếp trong route handler cho logic phức tạp → tạo service
- ❌ Quên `flush_data()` sau khi write vào storage
- ❌ Import model với prefix `api.core.models` → dùng `from core.models import ...`
- ❌ Hardcode database path → dùng env var hoặc parameter
