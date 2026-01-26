# Story Creator API Documentation

## Swagger UI

Sau khi chạy API backend, truy cập Swagger UI tại:

**http://localhost:5000/api/docs**

## Quick Start

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Chạy API server:
```bash
python main.py -i api
```

3. Truy cập Swagger UI:
```
http://localhost:5000/api/docs
```

## API Endpoints Overview

### Health Check
- `GET /api/health` - Kiểm tra trạng thái server

### Worlds Management
- `GET /api/worlds` - Lấy danh sách thế giới
- `POST /api/worlds` - Tạo thế giới mới
- `GET /api/worlds/{world_id}` - Chi tiết thế giới
- `DELETE /api/worlds/{world_id}` - Xóa thế giới
- `GET /api/worlds/{world_id}/stories` - Câu chuyện trong thế giới
- `GET /api/worlds/{world_id}/characters` - Nhân vật trong thế giới
- `GET /api/worlds/{world_id}/locations` - Địa điểm trong thế giới
- `GET /api/worlds/{world_id}/relationships` - Sơ đồ quan hệ SVG

### Stories Management
- `GET /api/stories` - Lấy tất cả câu chuyện
- `POST /api/stories` - Tạo câu chuyện mới
- `GET /api/stories/{story_id}` - Chi tiết câu chuyện
- `DELETE /api/stories/{story_id}` - Xóa câu chuyện

### GPT Integration
- `POST /api/gpt/analyze` - Phân tích mô tả với GPT
- `GET /api/gpt/results/{task_id}` - Lấy kết quả GPT

### Statistics
- `GET /api/stats` - Thống kê hệ thống

## Request Examples

### 1. Create World

**POST** `/api/worlds`

```json
{
  "name": "Vương quốc Eldoria",
  "world_type": "fantasy",
  "description": "Một vương quốc cổ đại với 3 vị vua, 5 thành phố lớn, và nhiều sinh vật thần bí"
}
```

**Response (201):**
```json
{
  "world_id": "uuid-123",
  "name": "Vương quốc Eldoria",
  "world_type": "fantasy",
  "description": "...",
  "entities": ["entity-id-1", "entity-id-2"],
  "locations": ["location-id-1", "location-id-2"],
  "stories": []
}
```

### 2. GPT Analysis

**POST** `/api/gpt/analyze`

```json
{
  "world_description": "Một vương quốc với 3 vị vua, 5 thành phố lớn và rừng rậm nguy hiểm",
  "world_type": "fantasy"
}
```

**Response (200):**
```json
{
  "task_id": "task-uuid-456"
}
```

**Poll for results:** `GET /api/gpt/results/task-uuid-456`

**Response when completed:**
```json
{
  "status": "completed",
  "result": {
    "entities": [
      {
        "name": "Vua Arthur",
        "entity_type": "king",
        "description": "Vị vua trị vì công bằng"
      }
    ],
    "locations": [
      {
        "name": "Thành phố Camelot",
        "description": "Thủ đô của vương quốc",
        "coordinates": {"x": 10, "y": 20}
      }
    ]
  }
}
```

### 3. Create Story

**POST** `/api/stories`

```json
{
  "world_id": "uuid-123",
  "title": "Cuộc phiêu lưu của John",
  "description": "John khám phá khu rừng bí ẩn và gặp Vua Arthur",
  "genre": "adventure",
  "time_index": 10
}
```

**Response (201):**
```json
{
  "story": {
    "story_id": "story-uuid-789",
    "title": "Cuộc phiêu lưu của John",
    "world_id": "uuid-123",
    "genre": "adventure",
    "entities": ["entity-id-john", "entity-id-arthur"],
    "locations": ["location-id-forest"]
  },
  "time_cone": {
    "time_cone_id": "tc-uuid-999",
    "time_index": 10,
    "story_id": "story-uuid-789"
  }
}
```

### 4. Get World Details

**GET** `/api/worlds/uuid-123`

**Response (200):**
```json
{
  "world_id": "uuid-123",
  "name": "Vương quốc Eldoria",
  "world_type": "fantasy",
  "description": "...",
  "entities": [...],
  "locations": [...],
  "stories": [...]
}
```

### 5. Get Statistics

**GET** `/api/stats`

**Response (200):**
```json
{
  "total_worlds": 10,
  "total_stories": 25,
  "total_entities": 50,
  "total_locations": 30,
  "has_gpt": true,
  "storage_type": "NoSQL Database"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Tên thế giới là bắt buộc khi sử dụng GPT"
}
```

### 404 Not Found
```json
{
  "error": "World not found"
}
```

### 503 Service Unavailable
```json
{
  "error": "GPT not available"
}
```

## Data Models

### World
```json
{
  "world_id": "string (uuid)",
  "name": "string",
  "world_type": "fantasy|sci-fi|modern|historical",
  "description": "string",
  "entities": ["entity_id_1", "entity_id_2"],
  "locations": ["location_id_1", "location_id_2"],
  "stories": ["story_id_1", "story_id_2"],
  "metadata": {
    "created_at": "ISO timestamp"
  }
}
```

### Story
```json
{
  "story_id": "string (uuid)",
  "title": "string",
  "world_id": "string (uuid)",
  "genre": "adventure|mystery|conflict|discovery",
  "description": "string",
  "entities": ["entity_id_1"],
  "locations": ["location_id_1"],
  "time_cones": ["time_cone_id_1"]
}
```

### Entity (Character)
```json
{
  "entity_id": "string (uuid)",
  "name": "string",
  "entity_type": "string (e.g., 'hero', 'king', 'wizard')",
  "description": "string",
  "world_id": "string (uuid)",
  "attributes": {
    "Strength": "integer (0-10)",
    "Intelligence": "integer (0-10)",
    "Charisma": "integer (0-10)"
  }
}
```

### Location
```json
{
  "location_id": "string (uuid)",
  "name": "string",
  "description": "string",
  "world_id": "string (uuid)",
  "coordinates": {
    "x": "float",
    "y": "float"
  }
}
```

## CORS Configuration

API hỗ trợ CORS cho React frontend:

- **Allowed Origins**: `http://localhost:3000`, `http://127.0.0.1:3000`
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers**: Content-Type

## Rate Limiting

Hiện tại không có rate limiting. Trong production nên thêm rate limiting để bảo vệ API.

## Authentication

Hiện tại API không yêu cầu authentication. Trong production nên thêm:
- API Keys
- JWT tokens
- OAuth 2.0

## Testing API

### Using curl

```bash
# Health check
curl http://localhost:5000/api/health

# Get all worlds
curl http://localhost:5000/api/worlds

# Create world
curl -X POST http://localhost:5000/api/worlds \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test World",
    "world_type": "fantasy",
    "description": "A test world"
  }'
```

### Using Swagger UI

1. Mở http://localhost:5000/api/docs
2. Click vào endpoint muốn test
3. Click "Try it out"
4. Nhập parameters
5. Click "Execute"
6. Xem response

### Using Postman

Import Swagger JSON:
1. Mở Postman
2. Import → Link
3. Paste: `http://localhost:5000/apispec.json`
4. Import collection

## Troubleshooting

### Swagger UI không hiển thị
- Kiểm tra `flasgger` đã được cài đặt: `pip install flasgger`
- Restart server

### CORS errors
- Đảm bảo frontend chạy trên port 3000
- Kiểm tra Flask-CORS đã được cài đặt

### GPT endpoints trả về 503
- Kiểm tra file `.env` có `OPENAI_API_KEY`
- Chạy `python test_api_key.py` để verify

## Next Steps

- [ ] Add authentication
- [ ] Add rate limiting
- [ ] Add request validation with marshmallow
- [ ] Add pagination for large datasets
- [ ] Add filtering and sorting
- [ ] Add WebSocket support for real-time updates
- [ ] Add API versioning (/api/v1/, /api/v2/)
