# Story Creator - React + API Architecture Guide

## 📋 Tổng quan

Story Creator đã được chuyển đổi từ Flask template-based sang kiến trúc **React Frontend + REST API Backend**.

### Kiến trúc mới (Khuyến nghị)

```
┌─────────────────────────────────────────────────────┐
│              React Frontend (Port 3000)             │
│   - TailwindCSS + DaisyUI                          │
│   - React Router for navigation                    │
│   - Axios for API calls                            │
└────────────────┬────────────────────────────────────┘
                 │ HTTP/REST API
                 │
┌────────────────▼────────────────────────────────────┐
│          Flask API Backend (Port 5000)              │
│   - Pure REST API (no templates)                   │
│   - CORS enabled for React                         │
│   - GPT Service integration                        │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│         Storage Layer (TinyDB/JSON)                 │
│   - NoSQL: TinyDB (default, faster)                │
│   - JSON: File-based (legacy)                      │
└─────────────────────────────────────────────────────┘
```

### Kiến trúc cũ (Legacy)

```
Flask Templates (Port 5000) → Storage
```

## 🚀 Setup nhanh

### 1. Cài đặt dependencies

```bash
# Backend (Python)
pip install -r requirements.txt

# Frontend (Node.js)
npm install
cd ..

# Hoặc cài tất cả cùng lúc
npm run install:all
```

### 2. Chạy ứng dụng

**Cách 1: Sử dụng npm script (Khuyến nghị)**
```bash
npm run dev
```

**Cách 2: Chạy thủ công (2 terminals)**

Terminal 1 - Backend:
```bash
python api/main.py -i api
```

Terminal 2 - Frontend:
```bash
npm run dev
```

### 3. Truy cập ứng dụng

- Frontend: http://localhost:3000
- API Backend: http://localhost:5000/api
- Health Check: http://localhost:5000/api/health

## 📁 Cấu trúc thư mục

```
story-creator/
├── app/                        # Next.js app router (pages, layouts)
├── src/                        # React components and client code
│   ├── components/            # UI components
│   │   ├── Navbar.jsx
│   │   ├── Toast.jsx
│   │   ├── LoadingSpinner.jsx
│   │   └── timeline/          # ⚡ Event Timeline (React Flow)
│   │       ├── EventTimelineSection.jsx  # Lazy-loaded section
│   │       ├── TimelineCanvas.jsx        # React Flow canvas
│   │       ├── EventNode.jsx             # Custom event node
│   │       ├── YearCluster.jsx           # Year label node
│   │       ├── ConnectionLine.jsx        # Custom edge
│   │       └── TimelineControls.jsx      # Zoom/direction controls
│   ├── containers/            # Data fetching containers
│   │   ├── EventTimelineContainer.jsx  # Timeline data + GPT extraction
│   │   ├── StoryDetailContainer.jsx
│   │   └── WorldDetailContainer.jsx
│   ├── views/                 # Page-level view components
│   ├── services/              # API client
│   │   └── api.js
│   └── index.css              # Global styles
├── package.json
├── next.config.js             # Next.js configuration
└── tailwind.config.js         # TailwindCSS config
│
├── interfaces/
│   ├── api_backend.py         # ✨ NEW: Pure REST API
│   ├── api/interfaces/api_backend.py       # LEGACY: Template-based
│   └── simulation_interface.py
│
├── services/                  # Business logic layer
│   ├── gpt_service.py        # GPT operations
│   └── character_service.py  # Character utilities
│
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── package.json              # Root package.json
├── QUICK_START_REACT.md      # Quick reference
└── README.md
```

## 🔌 API Endpoints

### Health & Stats
- `GET /api/health` - Server health check
- `GET /api/stats` - System statistics

### Worlds
- `GET /api/worlds` - List all worlds
- `POST /api/worlds` - Create new world
  ```json
  {
    "name": "World name",
    "world_type": "fantasy|sci-fi|modern|historical",
    "description": "World description",
    "gpt_entities": { ... } // Optional GPT analysis result
  }
  ```
- `GET /api/worlds/<id>` - Get world details
- `DELETE /api/worlds/<id>` - Delete world (not implemented yet)
- `GET /api/worlds/<id>/stories` - Get stories in world
- `GET /api/worlds/<id>/characters` - Get characters in world
- `GET /api/worlds/<id>/locations` - Get locations in world
- `GET /api/worlds/<id>/relationships` - Get relationship diagram

### Stories
- `GET /api/stories` - List all stories
- `POST /api/stories` - Create new story
  ```json
  {
    "world_id": "uuid",
    "title": "Story title",
    "description": "Story description",
    "genre": "adventure|mystery|conflict|discovery",
    "time_index": 0-100
  }
  ```
- `GET /api/stories/<id>` - Get story details
- `DELETE /api/stories/<id>` - Delete story (not implemented yet)

### GPT Integration
- `POST /api/gpt/analyze` - Analyze world description
  ```json
  {
    "world_description": "Description text",
    "world_type": "fantasy"
  }
  ```
  Returns: `{ "task_id": "uuid" }`

- `GET /api/gpt/results/<task_id>` - Get GPT analysis results
  ```json
  {
    "status": "pending|completed|error",
    "result": { "entities": [...], "locations": [...] }
  }
  ```

## 🛠️ Development Workflow

### Frontend Development

```bash

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

**File structure:**
- `src/pages/` - Add new pages here
- `src/components/` - Add reusable components
- `src/components/timeline/` - Event Timeline components (React Flow)
- `src/containers/` - Data fetching containers
- `src/services/api.js` - Add new API endpoints

### Event Timeline Feature

Dashboard có một section "Timeline Sự kiện" sử dụng React Flow (`@xyflow/react`) để hiển thị các sự kiện được trích xuất từ câu chuyện bằng GPT.

**Luồng dữ liệu:**
1. User chọn World từ dropdown → `EventTimelineContainer` gọi `GET /api/worlds/:id/events`
2. User nhấn "Trích xuất sự kiện" → `POST /api/worlds/:id/events/extract` (async GPT)
3. Container polls `GET /api/gpt/results/:taskId` mỗi 2 giây
4. Timeline data → `TimelineCanvas` → React Flow nodes/edges

**Caching:** GPT analysis được cache bằng SHA-256 hash của story content. `?force=true` để bỏ qua cache.

**Event click:** Navigate tới `/stories/:storyId?event=:eventId&position=:pos` → StoryDetailView scroll & highlight đoạn văn liên quan.

### Backend Development

```bash
# Run API server
python api/main.py -i api

# Run with debug mode
python api/main.py -i api --debug

# Run legacy template mode
python api/main.py -i api

# Run simulation mode
python api/main.py -i simulation
```

**Adding new endpoints:**
Edit `api/interfaces/api_backend.py` and add routes in `_register_routes()` method.

### Service Layer

Business logic được tách riêng trong `services/`:

```python
# GPT operations
from services import GPTService

gpt_service = GPTService(gpt_client)
gpt_service.generate_world_description(
    world_type="fantasy",
    callback_success=on_success,
    callback_error=on_error
)

# Character utilities
from services import CharacterService

names, ids = CharacterService.detect_mentioned_characters(
    description, entity_data_list
)
```

## Frontend Tech Stack

- **React** 18.2 - UI library
- **React Router** 6.20 - Client-side routing
- **Axios** 1.6 - HTTP client for API calls
- **TailwindCSS** 3.4 - Utility-first CSS framework
- **DaisyUI** 4.6 - Pre-built components
- **Vite** 5.0 - Fast build tool & dev server
- **@heroicons/react** 2.2 - SVG icon components (thay thế text/emoji icons)
- **@xyflow/react** 12.10 - React Flow cho Event Timeline

### Key Features

1. **Component-based UI**: Modular, reusable components
2. **Client-side routing**: Fast navigation without page reloads
3. **Code-splitting & Lazy loading**: Route-level `React.lazy()` + `Suspense`
4. **Vendor chunk splitting**: `manualChunks` trong `vite.config.js` (react, xyflow, ui)
5. **Real-time updates**: Toast notifications for user feedback
6. **Responsive design**: Mobile-friendly with TailwindCSS
7. **Async GPT integration**: Non-blocking UI during AI processing
8. **Heroicons**: Tất cả icon dùng `@heroicons/react/24/outline` (không dùng text/emoji)

## 🔧 Backend Tech Stack

- **Flask** 3.0 - Lightweight web framework
- **Flask-CORS** 4.0 - CORS support for React
- **TinyDB** 4.8 - NoSQL database (default)
- **OpenAI** 1.0 - GPT-4o-mini integration
- **psutil** 5.9 - Process management

### Service Pattern

**Before (tightly coupled):**
```python
# In api/interfaces/api_backend.py
description = self.gpt.generate_world_description(world_type)
```

**After (service layer):**
```python
# In api_backend.py
self.gpt_service.generate_world_description(
    world_type=world_type,
    callback_success=lambda desc: self.gpt_results[task_id] = desc,
    callback_error=lambda err: self.gpt_results[task_id] = err
)
```

## 🔐 Environment Configuration

### Backend (.env)
```env
OPENAI_API_KEY=sk-...your-api-key
```

### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:5000/api
```

## 🐛 Troubleshooting

### Port conflicts

**Problem:** Port 5000 hoặc 3000 đã được sử dụng

**Solution:**
- Backend tự động kill process trên port 5000
- Frontend: Thay đổi port trong `vite.config.js`:
  ```js
  server: { port: 3001 }
  ```

### CORS errors

**Problem:** `Access-Control-Allow-Origin` error

**Solution:**
1. Cài đặt Flask-CORS: `pip install Flask-CORS`
2. Kiểm tra backend chạy trên port 5000
3. Kiểm tra frontend origin trong `api_backend.py`:
   ```python
   CORS(self.app, resources={
       r"/api/*": {"origins": ["http://localhost:3000"]}
   })
   ```

### GPT không hoạt động

**Problem:** GPT analysis không trả về kết quả

**Solution:**
1. Kiểm tra API key: `python api/test_api_key.py`
2. Tạo file `.env` với `OPENAI_API_KEY`
3. Kiểm tra quota OpenAI
4. Xem backend logs cho errors

### Build errors

**Problem:** `npm run build` fails

**Solution:**
```bash
# Clear cache và reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 📝 Migration from Legacy

Nếu bạn đang sử dụng web interface cũ:

1. **Legacy mode vẫn hoạt động:**
   ```bash
   python api/main.py -i api
   ```

2. **Migrate sang API mode:**
   - Dữ liệu database tương thích 100%
   - Chỉ cần chuyển interface mode

3. **Advantages of React:**
   - Faster UI updates
   - Better user experience
   - Easier to customize
   - Modern development workflow
   - Component reusability

## 🚢 Deployment

### Development
```bash
npm run dev  # Runs both backend and frontend
```

### Production

**Backend:**
```bash
# Using gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "interfaces.api_backend:APIBackend().app"
```

**Frontend:**
```bash
npm run build
# Serve from ../static/dist/ using nginx/apache
```

**Docker (TODO):**
```dockerfile
# Coming soon...
```

## 📚 Learning Resources

- [React Documentation](https://react.dev)
- [TailwindCSS](https://tailwindcss.com)
- [DaisyUI Components](https://daisyui.com)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Vite Guide](https://vitejs.dev)

## 🤝 Contributing

Khi thêm features mới:

1. **Backend**: Add endpoint in `api_backend.py`
2. **Service**: Add business logic in `services/`
3. **Frontend**: Add API method in `services/api.js`
4. **UI**: Create component in `components/` or page in `pages/`
5. **Test**: Test API với curl/Postman và UI trong browser

## 📄 License

MIT License
