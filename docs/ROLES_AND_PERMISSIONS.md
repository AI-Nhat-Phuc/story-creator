# Hệ thống Phân quyền (Roles & Permissions)

## Tổng quan

Story Creator sử dụng hệ thống phân quyền dựa trên vai trò (Role-Based Access Control - RBAC) để quản lý quyền truy cập của người dùng.

## Các vai trò (Roles)

### 1. 👑 Admin (Quản trị viên)
- **Quyền**: Toàn quyền quản trị hệ thống
- **Quota**: Không giới hạn
  - Public worlds: 999999
  - Public stories: 999999
  - GPT requests/day: 999999
- **Permissions**:
  - Quản lý tất cả users
  - Xóa bất kỳ nội dung nào
  - Xem tất cả nội dung
  - Sử dụng GPT không giới hạn
  - Tất cả quyền của user thường

### 2. 🛡️ Moderator (Kiểm duyệt viên)
- **Quyền**: Quản lý nội dung và người dùng
- **Quota**:
  - Public worlds: 20
  - Public stories: 100
  - GPT requests/day: 500
- **Permissions**:
  - Xem danh sách users
  - Xóa nội dung vi phạm
  - Ban/unban users (trừ admin)
  - Xem tất cả nội dung
  - Tất cả quyền của user thường

### 3. ⭐ Premium (Người dùng cao cấp)
- **Quyền**: Tính năng mở rộng
- **Quota**:
  - Public worlds: 10
  - Public stories: 50
  - GPT requests/day: 200
- **Permissions**:
  - Sử dụng GPT không giới hạn
  - Quota tăng gấp 10 lần
  - Tất cả quyền của user thường

### 4. 👤 User (Người dùng thường)
- **Quyền**: Sử dụng cơ bản
- **Quota**:
  - Public worlds: 1
  - Public stories: 20
  - GPT requests/day: 50
- **Permissions**:
  - Tạo/sửa/xóa nội dung của mình
  - Chia sẻ nội dung riêng tư
  - Sử dụng GPT (có giới hạn)

### 5. 👁️ Guest (Khách)
- **Quyền**: Chỉ xem
- **Quota**: 0 (không thể tạo gì)
- **Permissions**:
  - Chỉ xem nội dung công khai

## API Endpoints

### Admin Routes (Yêu cầu Auth)

#### 1. Lấy danh sách users
```http
GET /api/admin/users?role=admin&search=username
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "success": true,
  "users": [
    {
      "user_id": "uuid",
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "metadata": {
        "public_worlds_count": 5,
        "public_worlds_limit": 999999
      }
    }
  ],
  "total": 1
}
```

#### 2. Đổi role user
```http
PUT /api/admin/users/{user_id}/role
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "role": "premium"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Đã đổi role từ user sang premium",
  "user": {
    "user_id": "uuid",
    "username": "john",
    "role": "premium",
    "quotas": {
      "public_worlds_limit": 10,
      "public_stories_limit": 50,
      "gpt_requests_per_day": 200
    }
  }
}
```

#### 3. Ban/Unban user
```http
POST /api/admin/users/{user_id}/ban
Authorization: Bearer {moderator_token}
Content-Type: application/json

{
  "banned": true,
  "reason": "Vi phạm nội dung"
}
```

#### 4. Lấy thông tin roles
```http
GET /api/admin/roles
Authorization: Bearer {moderator_token}
```

**Response:**
```json
{
  "success": true,
  "roles": [
    {
      "role": "admin",
      "label": "Quản trị viên",
      "icon": "👑",
      "badge_color": "badge-error",
      "description": "Toàn quyền quản trị hệ thống",
      "permissions": ["manage_users", "delete_any_content", ...],
      "quotas": {
        "public_worlds": 999999,
        "public_stories": 999999,
        "gpt_per_day": 999999
      }
    }
  ]
}
```

#### 5. Thống kê admin
```http
GET /api/admin/stats
Authorization: Bearer {moderator_token}
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_users": 100,
    "role_breakdown": {
      "admin": 1,
      "moderator": 2,
      "premium": 10,
      "user": 87
    },
    "banned_users": 3,
    "total_worlds": 500,
    "total_stories": 2000,
    "public_worlds": 300,
    "private_worlds": 200
  }
}
```

## Backend Implementation

### 1. Permission Constants (`api/core/permissions.py`)

```python
from core.permissions import Role, Permission, has_permission

# Check permission
if has_permission(user.role, Permission.MANAGE_USERS):
    # Allow action
    pass

# Get role quota
limit = get_role_quota(user.role, 'public_worlds_limit')
```

### 2. Decorators (`api/interfaces/auth_middleware.py`)

#### @token_required
Yêu cầu JWT token hợp lệ, lưu user vào `g.current_user`

```python
@app.route('/api/protected')
@token_required
def protected_route():
    user = g.current_user
    return jsonify({'user_id': user.user_id})
```

#### @admin_required
Chỉ admin mới truy cập được

```python
@app.route('/api/admin/users')
@token_required
@admin_required
def admin_only():
    return jsonify({'message': 'Admin panel'})
```

#### @moderator_required
Admin hoặc Moderator truy cập được

```python
@app.route('/api/moderate/content')
@token_required
@moderator_required
def moderate():
    return jsonify({'message': 'Moderation panel'})
```

#### @permission_required
Kiểm tra permissions cụ thể

```python
from core.permissions import Permission

@app.route('/api/gpt/unlimited')
@token_required
@permission_required(Permission.USE_GPT, Permission.USE_GPT_UNLIMITED)
def unlimited_gpt():
    return jsonify({'message': 'Unlimited GPT access'})
```

#### @role_required
Yêu cầu một trong các roles

```python
from core.permissions import Role

@app.route('/api/premium/features')
@token_required
@role_required(Role.ADMIN, Role.PREMIUM)
def premium_features():
    return jsonify({'features': [...]})
```

#### @optional_auth
Cho phép cả authenticated và anonymous

```python
@app.route('/api/public-data')
@optional_auth
def public_data():
    if hasattr(g, 'current_user'):
        # User logged in
        return jsonify({'personalized': True})
    else:
        # Anonymous
        return jsonify({'personalized': False})
```

### 3. User Model (`api/core/models/user.py`)

```python
from core.models.user import User

# Create user
user = User(username='john', email='john@example.com', password_hash='...', role='user')

# Check quota
if user.can_create_public_world():
    user.increment_public_worlds()
    storage.save_user(user.to_dict())

# Check GPT quota
if user.can_use_gpt():
    user.increment_gpt_requests()
    # Use GPT
```

## Frontend Implementation

### 1. Admin Panel (`src/pages/AdminPanel.jsx`)

Trang quản trị dành cho admin/moderator:
- Danh sách users với search và filter
- Đổi role với modal selection
- Ban/unban users
- Thống kê hệ thống

**Access:** `/admin` (chỉ admin/moderator)

### 2. Role Badge Component (`src/components/RoleBadge.jsx`)

```jsx
import RoleBadge from '../components/RoleBadge'

<RoleBadge role="admin" size="md" />
```

### 3. API Service (`src/services/api.js`)

```javascript
import { adminAPI } from '../services/api'

// Get all users
const users = await adminAPI.getAllUsers({ role: 'admin', search: 'john' })

// Change role
await adminAPI.changeUserRole(userId, 'premium')

// Ban user
await adminAPI.banUser(userId, true, 'Spam')

// Get roles info
const roles = await adminAPI.getRoles()

// Get admin stats
const stats = await adminAPI.getAdminStats()
```

### 4. Navigation (`src/components/Navbar.jsx`)

Link "Admin" chỉ hiện với admin/moderator:

```jsx
{isAuthenticated && (user?.role === 'admin' || user?.role === 'moderator') && (
  <li>
    <Link to="/admin">Admin</Link>
  </li>
)}
```

## Workflow

### 1. Đổi role user

1. Admin đăng nhập
2. Truy cập `/admin`
3. Tìm user cần đổi role
4. Click "Đổi role"
5. Chọn role mới từ modal
6. Quota tự động cập nhật theo role mới

### 2. Ban user

1. Moderator/Admin đăng nhập
2. Truy cập `/admin`
3. Click "Ban" trên user
4. Nhập lý do ban
5. Xác nhận
6. User bị ban không thể tạo nội dung mới

### 3. Nâng cấp lên Premium

Có 2 cách:
- **Admin manual:** Admin đổi role thành "premium"
- **Auto upgrade:** (Tương lai) Tích hợp payment gateway

## Security Notes

### Backend
- Tất cả admin routes đều có `@token_required` + role check
- Moderator không thể ban admin
- User không thể đổi role của chính mình
- Password hash không bao giờ trả về trong API response

### Frontend
- Admin panel redirect về `/` nếu không có quyền
- Admin link chỉ hiện khi `user.role === 'admin' || 'moderator'`
- React Router protect routes với check trong useEffect

## Testing

### 1. Tạo admin user

```python
# In Python console hoặc test file
from core.models.user import User
from storage import NoSQLStorage

storage = NoSQLStorage()
admin = User(
    username='admin',
    email='admin@example.com',
    password_hash='hashed_password',
    role='admin'
)
storage.save_user(admin.to_dict())
```

### 2. Test permissions

```python
from core.permissions import has_permission, Permission

assert has_permission('admin', Permission.MANAGE_USERS) == True
assert has_permission('user', Permission.MANAGE_USERS) == False
```

### 3. Test decorators

```bash
# Without token
curl http://localhost:5000/api/admin/users
# Response: 401 Unauthorized

# With user token
curl -H "Authorization: Bearer {user_token}" http://localhost:5000/api/admin/users
# Response: 403 Forbidden

# With admin token
curl -H "Authorization: Bearer {admin_token}" http://localhost:5000/api/admin/users
# Response: 200 OK with users list
```

## Migration Guide

Nếu bạn đã có users cũ và muốn cập nhật quota theo role:

```python
from storage import NoSQLStorage
from core.models.user import User

storage = NoSQLStorage()
users = storage.list_users()

for user_data in users:
    user = User.from_dict(user_data)
    user._init_role_quotas()  # Re-init quotas based on role
    storage.save_user(user.to_dict())
    print(f"Updated {user.username} ({user.role})")
```

## Permissions List

### Content Permissions
- `CREATE_WORLD` - Tạo thế giới
- `EDIT_OWN_WORLD` - Sửa thế giới của mình
- `DELETE_OWN_WORLD` - Xóa thế giới của mình
- `SHARE_WORLD` - Chia sẻ thế giới
- `CREATE_STORY` - Tạo câu chuyện
- `EDIT_OWN_STORY` - Sửa câu chuyện của mình
- `DELETE_OWN_STORY` - Xóa câu chuyện của mình
- `SHARE_STORY` - Chia sẻ câu chuyện

### Admin Permissions
- `MANAGE_USERS` - Quản lý users (create, edit, delete)
- `VIEW_USERS` - Xem danh sách users
- `BAN_USERS` - Ban/unban users
- `MANAGE_ALL_CONTENT` - Quản lý mọi nội dung
- `DELETE_ANY_CONTENT` - Xóa bất kỳ nội dung nào
- `VIEW_ALL_CONTENT` - Xem tất cả nội dung (kể cả private)

### Feature Permissions
- `USE_GPT` - Sử dụng GPT (có hạn mức)
- `USE_GPT_UNLIMITED` - Sử dụng GPT không giới hạn
- `UNLIMITED_PUBLIC_WORLDS` - Tạo thế giới công khai không giới hạn
- `UNLIMITED_PUBLIC_STORIES` - Tạo câu chuyện công khai không giới hạn
- `INCREASED_QUOTA` - Quota tăng gấp nhiều lần

## Roadmap

### Phase 1 (Completed) ✅
- Role definitions
- Permission system
- Admin routes
- Frontend admin panel

### Phase 2 (Planned)
- Email verification for new users
- Password reset flow
- User activity logs
- Content reporting system

### Phase 3 (Future)
- Payment integration for Premium
- Automatic role expiration
- Custom permissions per user
- Team/Organization accounts
