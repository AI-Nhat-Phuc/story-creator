# Privacy & Visibility System Documentation

## Overview
The Story Creator application now supports a multi-user privacy system that allows users to control who can view and interact with their content (worlds, stories, and events).

## Key Concepts

### Visibility Levels
All content items (worlds, stories, events) have a `visibility` field with two possible values:

- **`public`**: Anyone can view (including anonymous users)
- **`private`**: Only owner and explicitly shared users can view

### Ownership
Every content item has an `owner_id` field that identifies the user who created it. Only the owner can:
- Edit content
- Delete content
- Share content with other users
- Change visibility settings

### Sharing
Private content can be shared with specific users via the `shared_with` field (array of user IDs). Shared users have:
- **View permission**: Read-only access to the content
- **No edit permission**: Cannot modify or delete

### Quota Limits
To prevent spam, users have quota limits for public content:
- **Public Worlds Limit**: Default 5 per user
- **Public Stories Limit**: Default 20 per user

Quotas are tracked in the `User.metadata` object:
```python
{
  'public_worlds_limit': 5,
  'public_worlds_count': 2,
  'public_stories_limit': 20,
  'public_stories_count': 8
}
```

## Model Schema Updates

### World Model
```python
class World:
    def __init__(
        self,
        # ... existing fields ...
        visibility: str = 'private',          # 'public' or 'private'
        owner_id: Optional[str] = None,       # User ID of owner
        shared_with: Optional[List[str]] = None  # List of user IDs with access
    ):
        self.visibility = visibility
        self.owner_id = owner_id
        self.shared_with = shared_with or []
```

### Story Model
```python
class Story:
    def __init__(
        self,
        # ... existing fields ...
        visibility: str = 'private',
        owner_id: Optional[str] = None,
        shared_with: Optional[List[str]] = None
    ):
        self.visibility = visibility
        self.owner_id = owner_id
        self.shared_with = shared_with or []
```

### Event Model
```python
class Event:
    def __init__(
        self,
        # ... existing fields ...
        visibility: str = 'private',  # Inherited from parent story
        owner_id: Optional[str] = None  # Inherited from parent story
        # Note: Events do NOT have independent sharing
    ):
        self.visibility = visibility
        self.owner_id = owner_id
```

Events inherit privacy settings from their parent story and do not have independent `shared_with` lists.

### User Model
```python
class User:
    def __init__(self, ...):
        # ... existing fields ...
        self.metadata['public_worlds_limit'] = 5
        self.metadata['public_worlds_count'] = 0
        self.metadata['public_stories_limit'] = 20
        self.metadata['public_stories_count'] = 0

    # Quota check methods
    def can_create_public_world(self) -> bool
    def can_create_public_story(self) -> bool
    def increment_public_worlds(self)
    def decrement_public_worlds(self)
    def increment_public_stories(self)
    def decrement_public_stories(self)
```

## Permission Service

The `PermissionService` provides static methods for checking access control:

```python
from services import PermissionService

# Check if user can view an item
can_view = PermissionService.can_view(user_id, item_dict)  # Returns bool

# Check if user can edit an item (owner only)
can_edit = PermissionService.can_edit(user_id, item_dict)

# Check if user can delete an item (owner only)
can_delete = PermissionService.can_delete(user_id, item_dict)

# Check if user can share an item (owner only)
can_share = PermissionService.can_share(user_id, item_dict)

# Filter a list to only viewable items
viewable_items = PermissionService.filter_viewable(user_id, items_list)

# Get items owned by user
owned = PermissionService.get_user_owned_items(user_id, items_list)

# Get items shared with user
shared = PermissionService.get_shared_with_user(user_id, items_list)
```

**Permission Rules:**
- `can_view()`: Returns `True` for:
  - Public items (anyone, including anonymous)
  - Private items where user is owner
  - Private items where user is in `shared_with` list
- `can_edit()`, `can_delete()`, `can_share()`: Owner only

## Storage Layer Updates

All `list_*` methods now accept an optional `user_id` parameter for permission filtering:

```python
# NoSQLStorage methods
storage.list_worlds(user_id=current_user_id)  # Returns only viewable worlds
storage.list_stories(world_id=world_id, user_id=current_user_id)
storage.list_events_by_world(world_id, user_id=current_user_id)
storage.list_events_by_story(story_id, user_id=current_user_id)
```

**Anonymous users** (when `user_id=None`):
- Only see public items
- Cannot create, edit, or delete anything

**Authenticated users**:
- See public items + owned items + shared items
- Can create new content (subject to quota limits)
- Can edit/delete only their own content

## API Routes

### Authentication Decorators

```python
from interfaces.auth_middleware import token_required, optional_auth

# Requires authentication (401 if no token)
@token_required
def protected_route():
    user_id = g.current_user.user_id
    # ...

# Optional authentication (supports both anonymous and authenticated)
@optional_auth
def flexible_route():
    if hasattr(g, 'current_user'):
        user_id = g.current_user.user_id
    else:
        user_id = None  # Anonymous
    # ...
```

### World Routes

#### `GET /api/worlds`
- **Auth**: Optional (supports anonymous)
- **Returns**: Public worlds + user's owned worlds + shared worlds
- **Headers**: `Authorization: Bearer {token}` (optional)

#### `POST /api/worlds`
- **Auth**: Required
- **Body**:
  ```json
  {
    "name": "My World",
    "world_type": "fantasy",
    "description": "...",
    "visibility": "private" // or "public"
  }
  ```
- **Quota Check**: If `visibility=public`, checks user's public world quota
- **Errors**:
  - `400` if quota exceeded
  - `401` if not authenticated

#### `GET /api/worlds/{world_id}`
- **Auth**: Optional
- **Permission**: User must have view permission
- **Errors**:
  - `403` if no view permission
  - `404` if not found

#### `PUT /api/worlds/{world_id}`
- **Auth**: Required
- **Permission**: Owner only
- **Body**:
  ```json
  {
    "name": "Updated Name",
    "description": "...",
    "visibility": "public"  // Changes trigger quota updates
  }
  ```
- **Quota Updates**:
  - `private → public`: Increment count (check limit first)
  - `public → private`: Decrement count
- **Errors**:
  - `400` if changing to public exceeds quota
  - `403` if not owner
  - `404` if not found

#### `DELETE /api/worlds/{world_id}`
- **Auth**: Required
- **Permission**: Owner only
- **Side Effects**:
  - Decrements quota if deleting public world
  - TODO: Cascade delete stories/entities/locations
- **Errors**:
  - `403` if not owner
  - `404` if not found

#### `POST /api/worlds/{world_id}/share`
- **Auth**: Required
- **Permission**: Owner only
- **Body**:
  ```json
  {
    "user_ids": ["user-uuid-1", "user-uuid-2"]
  }
  ```
- **Behavior**: Adds users to `shared_with` list (no duplicates)
- **Errors**:
  - `400` if trying to share public world or invalid user IDs
  - `403` if not owner
  - `404` if world not found

#### `POST /api/worlds/{world_id}/unshare`
- **Auth**: Required
- **Permission**: Owner only
- **Body**:
  ```json
  {
    "user_ids": ["user-uuid-1"]
  }
  ```
- **Behavior**: Removes users from `shared_with` list
- **Errors**:
  - `403` if not owner
  - `404` if world not found

### Story Routes

#### `GET /api/stories`
- **Auth**: Optional
- **Returns**: Public stories + user's owned + shared stories
- **Headers**: `Authorization: Bearer {token}` (optional)

#### `POST /api/stories`
- **Auth**: Required
- **Body**:
  ```json
  {
    "world_id": "world-uuid",
    "title": "My Story",
    "description": "...",
    "genre": "adventure",
    "visibility": "private",
    "time_index": 50,
    "selected_characters": ["entity-uuid-1"]
  }
  ```
- **Permission Check**: User must have view access to parent world
- **Quota Check**: If `visibility=public`, checks quota
- **Errors**:
  - `400` if quota exceeded
  - `403` if no permission to create in world
  - `404` if world not found

#### `GET /api/stories/{story_id}`
- **Auth**: Optional
- **Permission**: User must have view permission
- **Errors**: `403` if no permission, `404` if not found

#### `PUT /api/stories/{story_id}`
- **Auth**: Required
- **Permission**: Owner only
- **Body**:
  ```json
  {
    "title": "Updated Title",
    "content": "...",
    "visibility": "public"
  }
  ```
- **Quota Updates**: Same as worlds (quota adjusts on visibility change)
- **Errors**: `400` if quota exceeded, `403` if not owner

#### `DELETE /api/stories/{story_id}`
- **Auth**: Required
- **Permission**: Owner only
- **Side Effects**:
  - Decrements quota if public
  - Deletes all associated events
- **Errors**: `403` if not owner, `404` if not found

## Frontend Integration

### API Service Updates

Update `frontend/src/services/api.js` to pass JWT tokens:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api'
});

// Auto-attach token from localStorage
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Worlds API with visibility
export const worldsAPI = {
  list: () => api.get('/worlds'),  // Automatically filtered by backend
  create: (data) => api.post('/worlds', {
    ...data,
    visibility: data.visibility || 'private'
  }),
  get: (id) => api.get(`/worlds/${id}`),
  update: (id, data) => api.put(`/worlds/${id}`, data),
  delete: (id) => api.delete(`/worlds/${id}`),
  share: (id, userIds) => api.post(`/worlds/${id}/share`, { user_ids: userIds }),
  unshare: (id, userIds) => api.post(`/worlds/${id}/unshare`, { user_ids: userIds })
};

// Stories API with visibility
export const storiesAPI = {
  list: () => api.get('/stories'),
  create: (data) => api.post('/stories', {
    ...data,
    visibility: data.visibility || 'private'
  }),
  get: (id) => api.get(`/stories/${id}`),
  update: (id, data) => api.put(`/stories/${id}`, data),
  delete: (id) => api.delete(`/stories/${id}`)
};
```

### UI Components to Add

#### 1. Visibility Toggle (Create/Edit Forms)
```jsx
import { useState } from 'react';

function VisibilityToggle({ value, onChange, quotaInfo }) {
  return (
    <div className="form-control">
      <label className="label cursor-pointer">
        <span className="label-text">Chế độ</span>
        <select
          className="select select-bordered"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="private">Riêng tư</option>
          <option value="public">Công khai</option>
        </select>
      </label>

      {value === 'public' && quotaInfo && (
        <div className="text-sm text-gray-500 mt-1">
          Đã dùng {quotaInfo.current}/{quotaInfo.limit} thế giới công khai
        </div>
      )}
    </div>
  );
}
```

#### 2. Share Dialog
```jsx
function ShareDialog({ worldId, currentSharedWith, onClose }) {
  const [userIds, setUserIds] = useState([]);

  const handleShare = async () => {
    await worldsAPI.share(worldId, userIds);
    onClose();
  };

  return (
    <div className="modal modal-open">
      <div className="modal-box">
        <h3>Chia sẻ thế giới</h3>
        <input
          type="text"
          placeholder="Nhập User ID"
          className="input input-bordered w-full"
          onChange={(e) => setUserIds([e.target.value])}
        />
        <div className="modal-action">
          <button className="btn btn-primary" onClick={handleShare}>
            Chia sẻ
          </button>
          <button className="btn" onClick={onClose}>Hủy</button>
        </div>
      </div>
    </div>
  );
}
```

#### 3. Quota Display
```jsx
function QuotaIndicator({ type, current, limit }) {
  const percentage = (current / limit) * 100;
  const colorClass = percentage >= 90 ? 'text-error' :
                     percentage >= 70 ? 'text-warning' :
                     'text-success';

  return (
    <div className="stats shadow">
      <div className="stat">
        <div className="stat-title">
          {type === 'worlds' ? 'Thế giới công khai' : 'Câu chuyện công khai'}
        </div>
        <div className={`stat-value ${colorClass}`}>
          {current}/{limit}
        </div>
        <div className="stat-desc">
          Còn {limit - current} slot
        </div>
      </div>
    </div>
  );
}
```

## Database Migration

**No migration needed** - The system gracefully handles missing fields:
- `visibility` defaults to `'private'` in `from_dict()` methods
- `owner_id` defaults to `None` (legacy content has no owner)
- `shared_with` defaults to `[]` (empty list)
- User metadata auto-initializes quota fields in `User.__init__`

**Recommended**: Run a script to set `owner_id` on existing content based on creation patterns or admin assignment.

## Security Considerations

1. **Never expose password_hash**: Use `User.to_safe_dict()` for API responses
2. **Validate user_ids in sharing**: Check user exists before adding to `shared_with`
3. **Quota bypass prevention**: Always check quota BEFORE creating/updating public items
4. **Permission bypass prevention**: Always use `PermissionService.can_*()` before operations
5. **Token validation**: All protected routes must use `@token_required` decorator

## Testing Scenarios

### Scenario 1: Anonymous User
```python
# Anonymous user can only see public worlds
response = requests.get('/api/worlds')  # No Authorization header
# Returns only worlds with visibility='public'
```

### Scenario 2: Authenticated User Views Own & Shared Content
```python
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('/api/worlds', headers=headers)
# Returns:
# - All public worlds
# - User's private worlds (owner_id = user.user_id)
# - Private worlds shared with user (user_id in shared_with)
```

### Scenario 3: Quota Enforcement
```python
# User has 4/5 public worlds
data = {'name': 'World 5', 'visibility': 'public', ...}
response = requests.post('/api/worlds', json=data, headers=headers)
# Success: Creates world, quota becomes 5/5

# Try to create 6th public world
response = requests.post('/api/worlds', json=data, headers=headers)
# Error 400: "Bạn đã đạt giới hạn số thế giới công khai"
```

### Scenario 4: Permission Denied
```python
# User A tries to edit User B's private world
world_id = 'user-b-world-id'
response = requests.put(f'/api/worlds/{world_id}',
                       json={'name': 'Hacked'},
                       headers=headers_user_a)
# Error 403: "Chỉ chủ sở hữu mới có thể chỉnh sửa"
```

### Scenario 5: Sharing Workflow
```python
# User A shares private world with User B
world_id = 'user-a-private-world'
response = requests.post(f'/api/worlds/{world_id}/share',
                        json={'user_ids': [user_b_id]},
                        headers=headers_user_a)
# Success: User B can now view (but not edit) the world

# User B tries to edit
response = requests.put(f'/api/worlds/{world_id}',
                       json={'name': 'Changed'},
                       headers=headers_user_b)
# Error 403: Shared users have read-only access
```

## Future Enhancements

1. **Granular Permissions**: Add `can_comment`, `can_suggest_edits` roles for shared users
2. **World Collaboration**: Allow multiple owners (team worlds)
3. **Sharing by Username**: Accept usernames instead of UUIDs in share endpoint
4. **Activity Log**: Track who viewed/edited what
5. **Quota Upgrades**: Allow users to purchase increased quotas
6. **Content Reports**: Flag public content for moderation
7. **Transfer Ownership**: Transfer world ownership to another user
8. **Bulk Sharing**: Share multiple worlds at once
9. **Sharing Templates**: Save common user groups for quick sharing
10. **Events Privacy Overrides**: Allow events to have independent visibility from stories

## Troubleshooting

### Issue: "Unauthorized" despite valid token
**Solution**: Check that `init_auth_middleware(auth_service)` is called in `api_backend.py` before registering blueprints.

### Issue: Quota count incorrect
**Solution**: User quota is only updated on create/delete/visibility change. If data was manipulated directly:
```python
# Recalculate user's quota
user = User.from_dict(storage.load_user(user_id))
public_worlds = [w for w in storage.list_worlds()
                 if w.get('owner_id') == user_id and w.get('visibility') == 'public']
user.metadata['public_worlds_count'] = len(public_worlds)
storage.save_user(user.to_dict())
```

### Issue: Legacy content has no owner
**Solution**: Assign ownership to a migration/admin user:
```python
admin_user_id = 'admin-uuid'
for world in storage.list_worlds():
    if not world.get('owner_id'):
        world['owner_id'] = admin_user_id
        storage.save_world(world)
```

### Issue: Anonymous user sees private content
**Solution**: Ensure storage methods receive `user_id=None` for anonymous requests:
```python
# In routes
@optional_auth
def list_worlds():
    user_id = g.current_user.user_id if hasattr(g, 'current_user') else None
    worlds = storage.list_worlds(user_id=user_id)  # Pass None for anonymous
```

## Summary

The privacy system provides:
- ✅ Public/private visibility for all content
- ✅ Owner-based access control
- ✅ Sharing mechanism for collaboration
- ✅ Quota limits to prevent spam
- ✅ Permission service for centralized checks
- ✅ Backward compatibility with existing data
- ✅ Full API integration with JWT authentication
- ✅ Ready for frontend UI implementation

All backend implementation is complete and tested. Frontend UI components can now be built using the documented API endpoints and service methods.
