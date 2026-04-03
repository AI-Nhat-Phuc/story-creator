# DESIGN — separate prod nonprod data

> **Status**: DRAFT
> **Phase**: DESIGN
> **Date**: 2026-04-03

---

## Changed Files

| File | Change Type | Maps to Spec Clause |
|------|-------------|---------------------|
| `api/utils/env_config.py` | NEW | BR-1, BR-2, BR-3, BR-4, Edge Cases |
| `api/app.py` | MODIFY | BR-1, BR-2, BR-3 |
| `api/main.py` | MODIFY | BR-1, BR-2, BR-3, BR-4 |
| `api/interfaces/api_backend.py` | MODIFY | BR-1, BR-2, BR-3 |
| `api/storage/mongo_storage.py` | MODIFY | BR-1, BR-2, BR-3 |

## Schema / Interface Changes

Không có thay đổi `api/schemas/` hay `api/core/models/`.
Đây là infrastructure change thuần túy.

## New Method Signatures

### `api/utils/env_config.py` (file mới — dùng chung cho app.py và main.py)

```python
def get_db_config() -> tuple[str, str]:
    """
    Trả về (db_path, mongo_db_name) dựa trên APP_ENV.

    APP_ENV=production  → ("story_creator_prod.db",   "story_creator_prod")
    APP_ENV=staging     → ("story_creator_staging.db", "story_creator_staging")
    APP_ENV=*           → ("story_creator.db",          "story_creator_dev")  [default]

    STORY_DB_PATH env var override db_path (BR-4).
    Vercel (/tmp prefix) được xử lý tự động.
    Invalid APP_ENV → fallback "development" + log warning (Edge Cases).
    """
```

## APIBackend Signature Change

```python
# TRƯỚC
def __init__(self, data_dir="data", storage_type="nosql", db_path="story_creator.db"):

# SAU (BR-1, BR-2, BR-3)
def __init__(self, data_dir="data", storage_type="nosql", db_path="story_creator.db", mongo_db_name="story_creator_dev"):
```

## MongoStorage Default DB Name Change

```python
# TRƯỚC
def __init__(self, mongodb_uri=None, db_name="story_creator"):

# SAU (BR-1 — prod = db name mới → fresh data tự nhiên)
def __init__(self, mongodb_uri=None, db_name="story_creator_dev"):
```

## Không thay đổi

- Tất cả API routes, services, schemas, models
- `STORY_DB_PATH` env var vẫn override (backward compat — BR-4)
- Local dev không bị ảnh hưởng (default vẫn là `story_creator.db`)
- Prod data fresh tự nhiên: `story_creator_prod` là db name mới, chưa có data (spec Behavior)
