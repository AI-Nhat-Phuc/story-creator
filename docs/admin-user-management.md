# Admin User Management

Two-panel admin UI (`/admin/users`) backed by three new Flask API endpoints.
The data layer uses an **in-memory mock** so the feature works out-of-the-box
with no additional infrastructure; swapping to MongoDB is a one-file change.

---

## Feature Overview

| Feature | Description |
|---------|-------------|
| **User list** | Searchable, filterable list of all registered users |
| **User detail** | Three-tab panel: Info, Permissions, Activity |
| **Permission overrides** | Grant or revoke individual permissions on top of role defaults |
| **Active / Inactive toggle** | Disable an account without banning it; enforced in the API layer |
| **Activity logs** | Per-user log of `create_story`, `update_story`, `delete_story` actions |

---

## API Endpoints

All endpoints require a valid admin or moderator JWT (`Authorization: Bearer <token>`).

### Toggle Active/Inactive Status

```
PUT /api/admin/users/{user_id}/status
Role required: admin
```

**Request body**
```json
{ "active": false }
```

**Response**
```json
{
  "success": true,
  "data": { "user_id": "...", "active": false },
  "message": "User marked as inactive"
}
```

**Enforcement** — `auth_middleware.token_required` now checks `metadata.active`
on every authenticated request. Inactive users receive HTTP 403.

---

### Update Permission Overrides

```
PUT /api/admin/users/{user_id}/permissions
Role required: admin
```

**Request body** — a dict of `{permission_name: bool}`. `true` grants the
permission regardless of role defaults; `false` revokes it. Send `{}` to clear
all overrides.

```json
{
  "permissions": {
    "use_gpt": true,
    "delete_any_content": false
  }
}
```

**Response**
```json
{
  "success": true,
  "data": {
    "user_id": "...",
    "custom_permissions": { "use_gpt": true, "delete_any_content": false }
  },
  "message": "Permissions updated"
}
```

Overrides are stored in `user.metadata.custom_permissions` (MongoDB / mongomock).

---

### Get User Activity Logs

```
GET /api/admin/users/{user_id}/activity-logs?limit=50
Role required: moderator or admin
```

**Response**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "log_id": "uuid",
        "user_id": "uuid",
        "action": "create_story",
        "resource_type": "story",
        "resource_id": "uuid",
        "metadata": { "title": "My Story", "visibility": "private" },
        "timestamp": "2025-05-03T12:00:00+00:00"
      }
    ],
    "total": 1
  }
}
```

---

## Data Structures

### User (relevant fields)

```python
{
  "user_id": str,           # UUID
  "username": str,
  "email": str,
  "role": str,              # admin | moderator | premium | user | guest
  "metadata": {
    "active": bool,               # NEW — false = account disabled (default true)
    "custom_permissions": dict,   # NEW — {permission_name: bool} overrides
    "banned": bool,
    "ban_reason": str,
    "gpt_enabled": bool,
    "public_worlds_count": int,
    "public_worlds_limit": int,
    "public_stories_count": int,
    "public_stories_limit": int,
  }
}
```

### ActivityLog entry

```python
{
  "log_id": str,            # UUID
  "user_id": str,           # UUID of the actor
  "action": str,            # create_story | update_story | delete_story
  "resource_type": str,     # always "story" for now
  "resource_id": str,       # UUID of the affected resource
  "metadata": dict,         # {"title": "...", "visibility": "..."}
  "timestamp": str,         # ISO 8601 UTC
}
```

### Permission override dict

```json
{ "permission_name": true | false }
```

Supported permission names (from `api/core/permissions.py`):

- `manage_users`, `view_users`, `ban_users`
- `manage_all_content`, `delete_any_content`, `view_all_content`
- `create_world`, `edit_own_world`, `delete_own_world`, `share_world`
- `create_story`, `edit_own_story`, `delete_own_story`, `share_story`
- `create_event`, `edit_own_event`, `delete_own_event`
- `use_gpt`, `use_gpt_unlimited`
- `unlimited_public_worlds`, `unlimited_public_stories`, `increased_quota`

---

## How the Mock Layer Works

Activity logs are stored in `ActivityLogService`, a module-level singleton
in `api/services/activity_log_service.py`. The store is a plain Python list
protected by a `threading.Lock`.

```
startup
  └── api_backend.py calls init_activity_log_service()
        └── creates ActivityLogService singleton

story created / updated / deleted
  └── story_routes.py calls get_activity_log_service().log(...)
        └── appends dict to _store (thread-safe)

GET /api/admin/users/{id}/activity-logs
  └── admin_routes.py calls activity_log_service.get_user_logs(user_id)
        └── filters + sorts _store in-memory
```

The mock layer is **per-process** and **non-persistent** — logs disappear on
server restart. This is intentional for the MVP; see below for production steps.

### Extending to Real DB

1. Open `api/services/activity_log_service.py`.
2. Replace the `_store` list in `ActivityLogService` with MongoDB calls:
   - `log()` → `collection.insert_one(entry)`
   - `get_user_logs()` → `collection.find({'user_id': user_id}).sort('timestamp', -1).limit(limit)`
   - `get_all_logs()` → `collection.find().sort('timestamp', -1).limit(limit)`
3. The public interface (`log / get_user_logs / get_all_logs`) is unchanged,
   so no other files need to be modified.

---

## Frontend Component Tree

```
/admin/users  (app/(main)/admin/users/page.jsx)
└── AdminUsersPage  (src/views/AdminUsersPage.jsx)
    ├── UserList  (src/components/admin/UserList.jsx)
    │   Search bar + scrollable list of user rows
    └── UserDetail  (src/components/admin/UserDetail.jsx)
        ├── [Info tab]
        │   User fields + active/inactive toggle button
        ├── [Permissions tab]
        │   └── PermissionEditor  (src/components/admin/PermissionEditor.jsx)
        │       Per-permission grant/revoke overrides + save
        └── [Activity tab]
            └── ActivityLogTable  (src/components/admin/ActivityLogTable.jsx)
                Tabular log entries with action badge + timestamp
```

All API calls go through `src/services/api.js` (`adminAPI.*`).  
No direct `fetch` or `axios` usage inside components.

---

## Running the E2E Tests

```bash
# Start dev server (both frontend + backend) first:
npm run dev

# In another terminal:
npm run test:e2e -- --grep "Admin User Management"

# Or run the specific file:
npx playwright test e2e/adminUserManagement.spec.cjs
```

Tests use programmatic admin login (no UI login flow) and are deterministic
because they re-activate any user they deactivate within the same test.
