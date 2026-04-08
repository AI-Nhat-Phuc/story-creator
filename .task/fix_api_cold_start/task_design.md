# DESIGN — Fix API Cold Start

> **Status**: DRAFT
> **Phase**: DESIGN
> **Date**: 2026-04-08

---

## Schema / Model Changes

**No changes to `api/schemas/` or `api/core/models/`.**

All changes are in the storage layer, service initialization, and frontend.
This section documents the interface contracts that guide the IMPLEMENT phase.

---

## Changed Files

| File | Change Type | Maps to Spec Clause |
|---|---|---|
| `api/storage/nosql_storage.py` | DELETE | BR-6 |
| `api/storage/json_storage.py` | DELETE | BR-6 |
| `api/storage/__init__.py` | MODIFY | BR-6 |
| `api/storage/mongo_storage.py` | MODIFY (lazy connect) | BR-5, EC-MongoDB |
| `api/utils/env_config.py` | MODIFY | BR-7 |
| `api/app.py` | MODIFY | Behavior-4 |
| `api/interfaces/api_backend.py` | MODIFY (lazy init) | Behavior-1,2,3 |
| `api/requirements.txt` | MODIFY (remove tinydb) | BR-6 |
| `frontend/src/hooks/useKeepAlive.js` | NEW | Behavior-5, BR-8,9,10 |
| `frontend/src/App.jsx` | MODIFY (mount hook) | Behavior-5 |

---

## 1. Storage Layer — `api/storage/`

### 1.1 Files to delete (spec §BR-6)

- `api/storage/nosql_storage.py` — TinyDB backend
- `api/storage/json_storage.py` — JSON file backend

### 1.2 `api/storage/__init__.py` new interface (spec §BR-6)

```python
# BEFORE
from .base_storage import BaseStorage
from .nosql_storage import NoSQLStorage
from .json_storage import Storage as JSONStorage
try:
    from .mongo_storage import MongoStorage
except ImportError:
    MongoStorage = None
__all__ = ['BaseStorage', 'NoSQLStorage', 'JSONStorage', 'MongoStorage']

# AFTER
from .base_storage import BaseStorage
from .mongo_storage import MongoStorage
__all__ = ['BaseStorage', 'MongoStorage']
```

### 1.3 `api/storage/mongo_storage.py` — lazy connect (spec §BR-5, §EC-MongoDB)

Current `__init__` opens a `MongoClient` connection immediately (line 63).
After change the constructor stores config only; the actual client is created on
first DB operation via a `_connect()` helper.

```python
# Constructor contract (no network I/O)
def __init__(self, mongodb_uri: str, db_name: str) -> None:
    self.uri = mongodb_uri
    self.db_name = db_name
    self.client = None   # not connected yet
    self.db = None
    self._lock = threading.Lock()

# Called automatically before any collection access
def _connect(self) -> None:
    """Open connection once; thread-safe double-checked locking."""
    if self.db is not None:
        return
    with self._lock:
        if self.db is not None:
            return
        self.client = MongoClient(self.uri, ...)
        self.db = self.client[self.db_name]
        self._init_collections()
        self._ensure_indexes()

# Every public method calls self._connect() as first line
def save_world(self, world_data):
    self._connect()
    ...
```

---

## 2. Env Config — `api/utils/env_config.py` (spec §BR-7)

`get_db_config()` returns a 2-tuple coupling TinyDB path + Mongo name.
After TinyDB removal it is replaced by two focused functions:

```python
# AFTER — replaces get_db_config()
def get_mongo_db_name() -> str:
    """Return MongoDB database name based on APP_ENV."""
    ...
    return mongo_db_name  # str only

def get_mongo_uri() -> str:
    """Return MONGODB_URI or raise RuntimeError (spec §BR-7)."""
    uri = os.environ.get('MONGODB_URI')
    if not uri:
        raise RuntimeError(
            "MONGODB_URI environment variable is required. "
            "Set it in your .env file or Vercel dashboard."
        )
    return uri
```

---

## 3. App Entrypoint — `api/app.py` (spec §Behavior-4)

```python
# BEFORE
db_path, mongo_db_name = get_db_config()
api = APIBackend(db_path=db_path, mongo_db_name=mongo_db_name)

# AFTER
from utils.env_config import get_mongo_uri, get_mongo_db_name
api = APIBackend(mongodb_uri=get_mongo_uri(), mongo_db_name=get_mongo_db_name())
```

---

## 4. `APIBackend.__init__` — lazy init contracts

### 4.1 Lazy GPT (spec §Behavior-1, §BR-1, §BR-4)

```python
# Module-level sentinels
_gpt_initialized = False
_gpt_lock = threading.Lock()

# Constructor: skip GPT entirely
self.gpt = None
self.gpt_service = None
self.event_service = EventService(None, self.storage)  # gpt=None is handled internally

# Lazy initializer (called by GPT routes)
def _ensure_gpt(self):
    global _gpt_initialized
    if _gpt_initialized:
        return
    with _gpt_lock:
        if _gpt_initialized:
            return
        try:
            self.gpt = GPTIntegration()
            self.gpt_service = GPTService(self.gpt)
            self.event_service = EventService(self.gpt, self.storage)
            self.has_gpt = True
        except (ImportError, ValueError):
            self.has_gpt = False
        _gpt_initialized = True
```

### 4.2 Lazy admin seeding (spec §Behavior-2, §BR-2, §BR-3)

```python
# Module-level flag
_admin_seeded = False

def _seed_once(self):
    global _admin_seeded
    if _admin_seeded:
        return
    _admin_seeded = True
    self._ensure_default_admin()
    self._seed_test_account()
```

A `before_request` hook registered in `APIBackend` calls `_seed_once()`,
skipping paths that start with `/api/health` or `/api/docs` (spec §BR-2).

### 4.3 Lazy Swagger (spec §Behavior-3)

```python
# Constructor: do NOT call Swagger(...)
self._swagger = None

# before_request hook (only triggers on /api/docs paths)
def _ensure_swagger(self):
    if self._swagger is None:
        self._swagger = Swagger(self.app, config=..., template=...)
```

---

## 5. Frontend keep-alive — `frontend/src/` (spec §Behavior-5, §BR-8,9,10)

New file `frontend/src/hooks/useKeepAlive.js`:

```js
// Contract
export function useKeepAlive(intervalMs = 300_000) {
    // - pings GET /api/health every intervalMs while visibilityState === "visible"
    // - silent: no toast, no state update, errors swallowed
    // - clears interval on unmount
    // - pauses on visibilitychange to "hidden", resumes on "visible"
}
```

Mounted once at the top of `frontend/src/App.jsx`:

```jsx
import { useKeepAlive } from './hooks/useKeepAlive'
// inside App():
useKeepAlive()
```

---

## Spec Clause Coverage

| Spec clause | Design section |
|---|---|
| Behavior-1 (lazy GPT) | §4.1 |
| Behavior-2 (lazy admin seeding) | §4.2 |
| Behavior-3 (lazy Swagger) | §4.3 |
| Behavior-4 (remove TinyDB, MongoDB only) | §1, §2, §3 |
| Behavior-5 (frontend keep-alive) | §5 |
| BR-1 (GPT once per process, thread-safe) | §4.1 |
| BR-2 (admin seeding skips health/docs) | §4.2 |
| BR-3 (admin seeding once per process) | §4.2 |
| BR-4 (GPT failure → non-GPT routes unaffected) | §4.1 |
| BR-5 (Mongo lazy connect, 503 on failure) | §1.3 |
| BR-6 (remove TinyDB/JSON storage files) | §1.1, §1.2 |
| BR-7 (MONGODB_URI required, fail fast) | §2 |
| BR-8,9,10 (keep-alive behavior) | §5 |
| EC-concurrent (thread-safe GPT init) | §4.1 |
| EC-health (health never triggers seeding) | §4.2 |
| EC-tab-hidden (pause on hidden) | §5 |
| EC-ping-failure (silent ignore) | §5 |
| EC-missing-MONGODB_URI (fail fast) | §2 |
| EC-MongoDB-failure (503, no TinyDB fallback) | §1.3 |
