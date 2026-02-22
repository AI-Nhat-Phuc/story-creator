# Swagger API Documentation - Setup Guide

## ✅ Đã hoàn thành

Swagger UI đã được tích hợp thành công vào Story Creator API!

## 📖 Truy cập Swagger UI

### 1. Chạy API backend
```bash
.venv\Scripts\python.exe api/main.py -i api
```

### 2. Mở trình duyệt
```
http://localhost:5000/api/docs
```

## 🎯 Features

### Swagger UI cung cấp:
- ✅ **Interactive API documentation** - Test API trực tiếp trong browser
- ✅ **Auto-generated docs** - Từ Python docstrings
- ✅ **Request/Response examples** - Ví dụ cho mọi endpoint
- ✅ **Model schemas** - Data structures rõ ràng
- ✅ **Try it out** - Execute API calls ngay trong UI
- ✅ **Export OpenAPI spec** - Tại `/apispec.json`

## 📋 Endpoints đã document

### Health
- `GET /api/health` - Server health check

### Worlds
- `GET /api/worlds` - List all worlds
- `POST /api/worlds` - Create new world
- `GET /api/worlds/{id}` - Get world details
- `DELETE /api/worlds/{id}` - Delete world
- `GET /api/worlds/{id}/stories` - World stories
- `GET /api/worlds/{id}/characters` - World characters
- `GET /api/worlds/{id}/locations` - World locations
- `GET /api/worlds/{id}/relationships` - Relationship diagram

### Stories
- `GET /api/stories` - List all stories
- `POST /api/stories` - Create new story
- `GET /api/stories/{id}` - Get story details
- `DELETE /api/stories/{id}` - Delete story

### GPT
- `POST /api/gpt/analyze` - Analyze with GPT
- `GET /api/gpt/results/{task_id}` - Get GPT results

### Stats
- `GET /api/stats` - System statistics

## 🔧 Cấu hình

### Swagger Config (trong api_backend.py)

```python
swagger_config = {
    "specs_route": "/api/docs",  # Swagger UI URL
    "swagger_ui": True,
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Story Creator API",
        "version": "1.0.0"
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http"],
    "tags": [
        {"name": "Health"},
        {"name": "Worlds"},
        {"name": "Stories"},
        {"name": "GPT"},
        {"name": "Stats"}
    ]
}
```

## 📝 Thêm documentation cho endpoint mới

### Format docstring:

```python
@self.app.route('/api/your-endpoint', methods=['GET', 'POST'])
def your_endpoint():
    """Endpoint description.
    ---
    tags:
      - YourTag
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            param1:
              type: string
              example: "value"
    responses:
      200:
        description: Success response
        schema:
          type: object
    """
    # Your code here
```

## 🚀 Testing trong Swagger UI

### Bước 1: Chọn endpoint
Click vào endpoint muốn test (ví dụ: `POST /api/worlds`)

### Bước 2: Try it out
Click button "Try it out"

### Bước 3: Nhập parameters
```json
{
  "name": "Test World",
  "world_type": "fantasy",
  "description": "A fantasy world for testing"
}
```

### Bước 4: Execute
Click "Execute" để gửi request

### Bước 5: Xem response
Response sẽ hiển thị ngay bên dưới với:
- Status code
- Response body
- Response headers

## 📤 Export API Spec

### OpenAPI JSON:
```
http://localhost:5000/apispec.json
```

### Import vào Postman:
1. Mở Postman
2. Import → Link
3. Paste: `http://localhost:5000/apispec.json`
4. Import collection

## 🎨 Customize Theme

Để thay đổi theme của Swagger UI, thêm vào config:

```python
swagger_config = {
    "swagger_ui_config": {
        "deepLinking": True,
        "displayRequestDuration": True,
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True
    }
}
```

## 🔐 Security (Production)

Trong production, nên bảo vệ Swagger UI:

```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == "admin" and password == "secret":
        return True
    return False

# Protect Swagger UI
@self.app.before_request
def before_request():
    if request.path.startswith('/api/docs'):
        return auth.login_required(lambda: None)()
```

## 📚 Tài liệu tham khảo

- [Flasgger Documentation](https://github.com/flasgger/flasgger)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)

## ✨ Benefits

### Cho Developers:
- Không cần viết docs riêng
- Auto-sync với code
- Interactive testing
- Clear examples

### Cho Users:
- Easy to understand API
- Try before integrate
- See all endpoints
- Clear request/response format

## 🐛 Troubleshooting

### Swagger UI không hiển thị
```bash
pip install flasgger
.venv\Scripts\python.exe api/main.py -i api
```

### Docstring không xuất hiện
- Kiểm tra format YAML trong docstring
- Đảm bảo indent đúng (2 spaces)

### Schema validation errors
- Kiểm tra OpenAPI spec syntax
- Validate tại: https://editor.swagger.io/

## 📈 Next Steps

- ✅ Basic Swagger UI working
- ⬜ Add request validation
- ⬜ Add authentication in docs
- ⬜ Add response examples
- ⬜ Add error responses
- ⬜ Version API (v1, v2)
