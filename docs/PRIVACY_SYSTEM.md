# Tài Liệu Hệ Thống Quyền Riêng Tư & Hiển Thị

## Tổng Quan
Story Creator hỗ trợ hệ thống quyền riêng tư đa người dùng cho phép người dùng kiểm soát ai có thể xem và tương tác với nội dung của họ (thế giới, câu chuyện và sự kiện).

## Các Khái Niệm Chính

### Mức Độ Hiển Thị
Tất cả các mục nội dung (thế giới, câu chuyện, sự kiện) đều có trường `visibility` với hai giá trị:

- **`public`**: Ai cũng có thể xem (kể cả người dùng ẩn danh)
- **`private`**: Chỉ chủ sở hữu và người dùng được chia sẻ mới có thể xem

### Quyền Sở Hữu
Mỗi mục nội dung có trường `owner_id` xác định người dùng đã tạo ra nó. Chỉ chủ sở hữu mới có thể:
- Chỉnh sửa nội dung
- Xóa nội dung
- Chia sẻ nội dung với người dùng khác
- Thay đổi cài đặt hiển thị

### Chia Sẻ
Nội dung riêng tư có thể được chia sẻ với người dùng cụ thể thông qua trường `shared_with` (mảng user ID). Người dùng được chia sẻ có:
- **Quyền xem**: Truy cập chỉ đọc vào nội dung
- **Không có quyền chỉnh sửa**: Không thể thay đổi hoặc xóa

### Giới Hạn Quota
Để ngăn chặn spam, người dùng có giới hạn quota cho nội dung công khai:
- **Giới hạn Thế giới Công khai**: Mặc định 5 thế giới/người dùng
- **Giới hạn Câu chuyện Công khai**: Mặc định 20 câu chuyện/người dùng

Quota được theo dõi trong đối tượng `User.metadata`:
```python
{
  'public_worlds_limit': 5,
  'public_worlds_count': 2,
  'public_stories_limit': 20,
  'public_stories_count': 8
}
```

## Cập Nhật Schema Model

### Model World
```python
class World:
    def __init__(
        self,
        # ... các trường hiện có ...
        visibility: str = 'private',          # 'public' hoặc 'private'
        owner_id: Optional[str] = None,       # User ID của chủ sở hữu
        shared_with: Optional[List[str]] = None  # Danh sách user ID có quyền truy cập
    ):
        self.visibility = visibility
        self.owner_id = owner_id
        self.shared_with = shared_with or []
```

### Model Story
```python
class Story:
    def __init__(
        self,
        # ... các trường hiện có ...
        visibility: str = 'private',
        owner_id: Optional[str] = None,
        shared_with: Optional[List[str]] = None
    ):
        self.visibility = visibility
        self.owner_id = owner_id
        self.shared_with = shared_with or []
```

### Model Event
```python
class Event:
    def __init__(
        self,
        # ... các trường hiện có ...
        visibility: str = 'private',  # Kế thừa từ câu chuyện cha
        owner_id: Optional[str] = None  # Kế thừa từ câu chuyện cha
        # Lưu ý: Event KHÔNG có chia sẻ độc lập
    ):
        self.visibility = visibility
        self.owner_id = owner_id
```

Event kế thừa cài đặt quyền riêng tư từ câu chuyện cha và không có danh sách `shared_with` độc lập.

### Model User
```python
class User:
    def __init__(self, ...):
        # ... các trường hiện có ...
        self.metadata['public_worlds_limit'] = 5
        self.metadata['public_worlds_count'] = 0
        self.metadata['public_stories_limit'] = 20
        self.metadata['public_stories_count'] = 0

    # Phương thức kiểm tra quota
    def can_create_public_world(self) -> bool
    def can_create_public_story(self) -> bool
    def increment_public_worlds(self)
    def decrement_public_worlds(self)
    def increment_public_stories(self)
    def decrement_public_stories(self)
```

## Dịch Vụ Phân Quyền

`PermissionService` cung cấp các phương thức tĩnh để kiểm tra kiểm soát truy cập:

```python
from services import PermissionService

# Kiểm tra xem người dùng có thể xem mục không
can_view = PermissionService.can_view(user_id, item_dict)  # Trả về bool

# Kiểm tra xem người dùng có thể chỉnh sửa (chỉ chủ sở hữu)
can_edit = PermissionService.can_edit(user_id, item_dict)

# Kiểm tra xem người dùng có thể xóa (chỉ chủ sở hữu)
can_delete = PermissionService.can_delete(user_id, item_dict)

# Kiểm tra xem người dùng có thể chia sẻ (chỉ chủ sở hữu)
can_share = PermissionService.can_share(user_id, item_dict)

# Lọc danh sách chỉ lấy các mục có thể xem
viewable_items = PermissionService.filter_viewable(user_id, items_list)

# Lấy các mục thuộc sở hữu của người dùng
owned = PermissionService.get_user_owned_items(user_id, items_list)

# Lấy các mục được chia sẻ với người dùng
shared = PermissionService.get_shared_with_user(user_id, items_list)
```

**Quy tắc phân quyền:**
- `can_view()`: Trả về `True` khi:
  - Mục công khai (ai cũng xem được, kể cả ẩn danh)
  - Mục riêng tư mà người dùng là chủ sở hữu
  - Mục riêng tư mà người dùng có trong danh sách `shared_with`
- `can_edit()`, `can_delete()`, `can_share()`: Chỉ chủ sở hữu

## Cập Nhật Tầng Storage

Tất cả các phương thức `list_*` chấp nhận tham số `user_id` tùy chọn để lọc theo quyền:

```python
# Phương thức NoSQLStorage
storage.list_worlds(user_id=current_user_id)  # Chỉ trả về thế giới có thể xem
storage.list_stories(world_id=world_id, user_id=current_user_id)
storage.list_events_by_world(world_id, user_id=current_user_id)
storage.list_events_by_story(story_id, user_id=current_user_id)
```

**Người dùng ẩn danh** (khi `user_id=None`):
- Chỉ thấy các mục công khai
- Không thể tạo, chỉnh sửa hoặc xóa bất cứ thứ gì

**Người dùng đã xác thực**:
- Thấy mục công khai + mục sở hữu + mục được chia sẻ
- Có thể tạo nội dung mới (theo giới hạn quota)
- Chỉ có thể chỉnh sửa/xóa nội dung của chính mình

## API Routes

### Decorator Xác Thực

```python
from interfaces.auth_middleware import token_required, optional_auth

# Yêu cầu xác thực (401 nếu không có token)
@token_required
def protected_route():
    user_id = g.current_user.user_id
    # ...

# Xác thực tùy chọn (hỗ trợ cả ẩn danh và đã xác thực)
@optional_auth
def flexible_route():
    if hasattr(g, 'current_user'):
        user_id = g.current_user.user_id
    else:
        user_id = None  # Ẩn danh
    # ...
```

### Routes Thế Giới

#### `GET /api/worlds`
- **Xác thực**: Tùy chọn (hỗ trợ ẩn danh)
- **Trả về**: Thế giới công khai + thế giới sở hữu + thế giới được chia sẻ

#### `POST /api/worlds`
- **Xác thực**: Bắt buộc
- **Body**:
  ```json
  {
    "name": "Thế giới của tôi",
    "world_type": "fantasy",
    "description": "...",
    "visibility": "private"
  }
  ```
- **Kiểm tra Quota**: Nếu `visibility=public`, kiểm tra quota thế giới công khai
- **Lỗi**:
  - `400` nếu vượt quá quota
  - `401` nếu chưa xác thực

#### `PUT /api/worlds/{world_id}`
- **Xác thực**: Bắt buộc
- **Quyền**: Chỉ chủ sở hữu
- **Cập nhật Quota**:
  - `private → public`: Tăng đếm (kiểm tra giới hạn trước)
  - `public → private`: Giảm đếm

#### `POST /api/worlds/{world_id}/share`
- **Xác thực**: Bắt buộc
- **Quyền**: Chỉ chủ sở hữu
- **Body**:
  ```json
  {
    "user_ids": ["user-uuid-1", "user-uuid-2"]
  }
  ```
- **Hành vi**: Thêm người dùng vào danh sách `shared_with` (không trùng lặp)

## Tích Hợp Frontend

### Cập Nhật API Service

```javascript
// frontend/src/services/api.js
import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

// Tự động đính kèm token từ localStorage
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const worldsAPI = {
  list: () => api.get('/worlds'),
  create: (data) => api.post('/worlds', { ...data, visibility: data.visibility || 'private' }),
  get: (id) => api.get(`/worlds/${id}`),
  update: (id, data) => api.put(`/worlds/${id}`, data),
  delete: (id) => api.delete(`/worlds/${id}`),
  share: (id, userIds) => api.post(`/worlds/${id}/share`, { user_ids: userIds }),
  unshare: (id, userIds) => api.post(`/worlds/${id}/unshare`, { user_ids: userIds })
};
```

### Các Component UI Cần Thêm

#### 1. Nút Chọn Chế Độ Hiển Thị
```jsx
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

#### 2. Hiển Thị Quota
```jsx
function QuotaIndicator({ type, current, limit }) {
  const percentage = (current / limit) * 100;
  const colorClass = percentage >= 90 ? 'text-error' :
                     percentage >= 70 ? 'text-warning' : 'text-success';
  return (
    <div className="stats shadow">
      <div className="stat">
        <div className="stat-title">
          {type === 'worlds' ? 'Thế giới công khai' : 'Câu chuyện công khai'}
        </div>
        <div className={`stat-value ${colorClass}`}>{current}/{limit}</div>
        <div className="stat-desc">Còn {limit - current} slot</div>
      </div>
    </div>
  );
}
```

## Tính Tương Thích Ngược

**Không cần migration** — Hệ thống xử lý các trường còn thiếu một cách linh hoạt:
- `visibility` mặc định là `'private'` trong các phương thức `from_dict()`
- `owner_id` mặc định là `None` (nội dung cũ không có chủ sở hữu)
- `shared_with` mặc định là `[]` (danh sách rỗng)
- Metadata người dùng tự khởi tạo các trường quota trong `User.__init__`

## Cân Nhắc Bảo Mật

1. **Không bao giờ tiết lộ password_hash**: Sử dụng `User.to_safe_dict()` cho phản hồi API
2. **Xác thực user_ids khi chia sẻ**: Kiểm tra người dùng tồn tại trước khi thêm vào `shared_with`
3. **Ngăn chặn bỏ qua quota**: Luôn kiểm tra quota TRƯỚC khi tạo/cập nhật mục công khai
4. **Ngăn chặn bỏ qua phân quyền**: Luôn dùng `PermissionService.can_*()` trước các thao tác
5. **Xác thực token**: Tất cả route được bảo vệ phải dùng decorator `@token_required`

## Xử Lý Sự Cố

### Vấn đề: "Unauthorized" mặc dù token hợp lệ
**Giải pháp**: Kiểm tra rằng `init_auth_middleware(auth_service)` được gọi trong `api_backend.py` trước khi đăng ký blueprints.

### Vấn đề: Số đếm quota không chính xác
**Giải pháp**: Tính toán lại quota của người dùng:
```python
user = User.from_dict(storage.load_user(user_id))
public_worlds = [w for w in storage.list_worlds()
                 if w.get('owner_id') == user_id and w.get('visibility') == 'public']
user.metadata['public_worlds_count'] = len(public_worlds)
storage.save_user(user.to_dict())
```

### Vấn đề: Nội dung cũ không có chủ sở hữu
**Giải pháp**: Gán quyền sở hữu cho tài khoản admin:
```python
admin_user_id = 'admin-uuid'
for world in storage.list_worlds():
    if not world.get('owner_id'):
        world['owner_id'] = admin_user_id
        storage.save_world(world)
```

## Tóm Tắt

Hệ thống quyền riêng tư cung cấp:
- ✅ Hiển thị công khai/riêng tư cho tất cả nội dung
- ✅ Kiểm soát truy cập dựa trên quyền sở hữu
- ✅ Cơ chế chia sẻ để cộng tác
- ✅ Giới hạn quota để ngăn chặn spam
- ✅ Dịch vụ phân quyền tập trung
- ✅ Tương thích ngược với dữ liệu hiện có
- ✅ Tích hợp API đầy đủ với xác thực JWT
