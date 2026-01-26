# Story Creator - React Frontend Setup

## Tổng quan

Frontend React cho Story Creator với API backend tách biệt hoàn toàn.

## Kiến trúc

```
frontend/               # React application
├── src/
│   ├── components/    # Reusable UI components
│   ├── pages/         # Page components (routes)
│   ├── services/      # API client
│   ├── App.jsx        # Main app component
│   └── main.jsx       # Entry point
└── package.json

interfaces/
├── api_backend.py     # Pure REST API (Flask)
└── web_interface.py   # Legacy template-based (deprecated)
```

## Yêu cầu hệ thống

- **Node.js**: >= 16.x
- **npm hoặc yarn**: >= 7.x
- **Python**: >= 3.7
- **pip**: Latest version

## Cài đặt

### 1. Cài đặt Backend (Python)

```bash
# Cài đặt dependencies Python
pip install -r requirements.txt

# Tạo file .env cho API key (nếu dùng GPT)
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 2. Cài đặt Frontend (React)

```bash
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt dependencies
npm install

# Hoặc sử dụng yarn
yarn install
```

## Chạy ứng dụng

### Development Mode

**Terminal 1 - Backend API:**
```bash
# Từ thư mục root
python main.py -i api

# Hoặc với debug mode
python main.py -i api --debug
```

Backend sẽ chạy tại: `http://localhost:5000/api`

**Swagger UI**: http://localhost:5000/api/docs

**Terminal 2 - React Frontend:**
```bash
# Từ thư mục frontend
cd frontend
npm run dev

# Hoặc
yarn dev
```

Frontend sẽ chạy tại: `http://localhost:3000`

### Production Build

```bash
# Build React app
cd frontend
npm run build

# Static files sẽ được tạo trong ../static/dist/
# Có thể serve bằng bất kỳ web server nào
```

## API Endpoints

### Health Check
- `GET /api/health` - Kiểm tra trạng thái server

### Worlds
- `GET /api/worlds` - Lấy danh sách thế giới
- `POST /api/worlds` - Tạo thế giới mới
- `GET /api/worlds/<id>` - Chi tiết thế giới
- `GET /api/worlds/<id>/stories` - Câu chuyện trong thế giới
- `GET /api/worlds/<id>/characters` - Nhân vật trong thế giới
- `GET /api/worlds/<id>/locations` - Địa điểm trong thế giới
- `GET /api/worlds/<id>/relationships` - Sơ đồ quan hệ

### Stories
- `GET /api/stories` - Lấy tất cả câu chuyện
- `POST /api/stories` - Tạo câu chuyện mới
- `GET /api/stories/<id>` - Chi tiết câu chuyện

### GPT
- `POST /api/gpt/analyze` - Phân tích mô tả thế giới
- `GET /api/gpt/results/<task_id>` - Lấy kết quả GPT

### Stats
- `GET /api/stats` - Thống kê hệ thống

## Cấu trúc Component

### Pages
- **Dashboard**: Trang chủ với thống kê
- **WorldsPage**: Quản lý thế giới
- **WorldDetailPage**: Chi tiết thế giới với tabs
- **StoriesPage**: Quản lý câu chuyện

### Components
- **Navbar**: Navigation bar
- **Toast**: Thông báo
- **LoadingSpinner**: Loading indicator

## Cấu hình

### Environment Variables

**Backend (.env):**
```env
OPENAI_API_KEY=your-api-key
```

**Frontend (.env.local):**
```env
VITE_API_URL=http://localhost:5000/api
```

### CORS

CORS đã được cấu hình trong `api_backend.py`:
- Cho phép origin: `http://localhost:3000`
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: Content-Type

## Troubleshooting

### Port 5000 đã được sử dụng
```bash
# API backend sẽ tự động kill process cũ
# Hoặc thủ công:
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### CORS errors
Đảm bảo:
1. Backend chạy trên port 5000
2. Frontend chạy trên port 3000
3. Flask-CORS đã được cài đặt: `pip install Flask-CORS`

### GPT không hoạt động
1. Kiểm tra file `.env` có `OPENAI_API_KEY`
2. Chạy test: `python test_api_key.py`
3. Kiểm tra quota OpenAI

## Development Tips

### Hot Reload
- React: Tự động reload khi sửa file `.jsx`
- Backend: Cần restart manually hoặc dùng `--debug` (không khuyến khích production)

### API Testing
```bash
# Sử dụng curl
curl http://localhost:5000/api/health

# Sử dụng Postman
Import collection từ docs/api_collection.json
```

### Debug
1. Backend: Xem console output hoặc dùng `--debug`
2. Frontend: F12 → Console/Network tab trong browser

## Deployment

### Backend
```bash
# Sử dụng gunicorn (production)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "interfaces.api_backend:APIBackend().app"
```

### Frontend
```bash
# Build và serve
cd frontend
npm run build

# Serve static files với nginx/apache
# Hoặc dùng serve
npx serve -s ../static/dist -l 3000
```

## Tech Stack

### Frontend
- **React** 18.2 - UI framework
- **React Router** 6.20 - Routing
- **Axios** 1.6 - HTTP client
- **TailwindCSS** 3.4 - Utility CSS
- **DaisyUI** 4.6 - Component library
- **Vite** 5.0 - Build tool

### Backend
- **Flask** 3.0 - Web framework
- **Flask-CORS** 4.0 - CORS support
- **TinyDB** 4.8 - NoSQL database
- **OpenAI** 1.0 - GPT integration
- **psutil** 5.9 - Process management

## License

MIT License
