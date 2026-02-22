# Story Creator

Hệ thống tạo thế giới và câu chuyện tương tác với **React Frontend + Flask API Backend**, deployed trên **Vercel** (monorepo). Tích hợp GPT-4o-mini cho mô phỏng nhân vật và sinh nội dung tự động.

🌐 **Live**: [story-creator-cyan.vercel.app](https://story-creator-cyan.vercel.app)

## Tính năng

- 🌍 Tạo và quản lý thế giới (Fantasy, Sci-Fi, Modern, Historical)
- 📖 Tạo câu chuyện với auto-detect nhân vật và liên kết thông minh
- 👥 Quản lý nhân vật với thuộc tính (Strength, Intelligence, Charisma)
- 📍 Quản lý địa điểm với tọa độ
- ⏰ Timeline theo nón ánh sáng (time cones)
- 🔗 Tự động liên kết câu chuyện qua nhân vật/địa điểm/thời gian chung
- 🤖 GPT-4o-mini: Sinh mô tả thế giới, phân tích nhân vật, mô phỏng quyết định
- 📊 Swagger UI cho API documentation
- 🚀 Deploy trên Vercel (monorepo: static frontend + serverless Python API)

## Quick Start

### Yêu cầu
- Python 3.7+ (khuyến nghị 3.10+)
- Node.js 18+
- (Tùy chọn) OpenAI API key cho GPT features

### Cài đặt

```bash
# Clone repo
git clone https://github.com/your-username/story-creator.git
cd story-creator

# Tạo virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows PowerShell
# source .venv/bin/activate          # macOS/Linux

# Cài đặt tất cả dependencies
npm run install:all

# Hoặc cài riêng:
pip install -r api/requirements.txt
cd frontend && npm install && cd ..
```

### Cấu hình (tùy chọn)

```bash
# Tạo file .env ở root cho GPT features
echo OPENAI_API_KEY=sk-your-key-here > .env
```

### Chạy ứng dụng

```bash
# Full stack (React + API) — KHUYẾN NGHỊ
npm run dev

# Hoặc chạy riêng:
# Terminal 1 — API Backend (port 5000)
.venv\Scripts\python.exe api/main.py -i api

# Terminal 2 — React Frontend (port 3000)
cd frontend && npm run dev
```

**Truy cập:**
- 🖥️ React UI: http://localhost:3000
- 📚 API Swagger: http://localhost:5000/api/docs

## Cấu trúc dự án (Monorepo)

```
story-creator/
├── api/                          # 🐍 Python backend
│   ├── app.py                    # Vercel serverless entrypoint
│   ├── main.py                   # Local dev entrypoint
│   ├── requirements.txt          # Python dependencies
│   ├── ai/                       # GPT-4o-mini integration
│   ├── core/models/              # Domain models (World, Story, Entity, Location, TimeCone)
│   ├── generators/               # Content generators + story linker
│   ├── interfaces/               # Flask API + blueprint routes
│   │   ├── api_backend.py        # Main Flask app (CORS, Swagger)
│   │   └── routes/               # world, story, gpt, health, stats
│   ├── services/                 # Business logic (GPTService, CharacterService)
│   ├── storage/                  # NoSQL (TinyDB) + JSON storage
│   └── visualization/            # Relationship diagrams
│
├── frontend/                     # ⚛️ React application
│   ├── src/
│   │   ├── components/           # UI components (GptButton, Modal, Toast, ...)
│   │   ├── containers/           # Data-fetching containers
│   │   ├── pages/                # Dashboard, Worlds, Stories, Detail pages
│   │   ├── services/api.js       # Centralized Axios API client
│   │   └── App.jsx               # Root component + React Router
│   ├── vite.config.js
│   └── package.json
│
├── docs/                         # 📖 Documentation
├── vercel.json                   # Vercel monorepo deployment config
├── package.json                  # Root npm scripts (concurrently)
└── .env                          # Environment variables
```

> **Lưu ý**: Tất cả Python code nằm trong `api/`. Import bên trong `api/` dùng bare module names (ví dụ: `from core.models import World`), KHÔNG dùng prefix `api.*`.

## API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/health` | Health check |
| GET | `/api/worlds` | Danh sách thế giới |
| POST | `/api/worlds` | Tạo thế giới mới |
| GET | `/api/worlds/<id>` | Chi tiết thế giới |
| GET | `/api/worlds/<id>/characters` | Danh sách nhân vật |
| GET | `/api/worlds/<id>/relationships` | Biểu đồ quan hệ |
| POST | `/api/stories` | Tạo câu chuyện |
| GET | `/api/stories/<id>` | Chi tiết câu chuyện |
| POST | `/api/gpt/analyze` | Phân tích GPT (async) |
| GET | `/api/gpt/results/<task_id>` | Kết quả GPT |
| GET | `/api/stats` | Thống kê hệ thống |

📚 Chi tiết đầy đủ tại Swagger UI: http://localhost:5000/api/docs

## Deploy lên Vercel

```bash
# Cài Vercel CLI
npm i -g vercel

# Deploy từ project root
vercel

# Production deploy
vercel --prod
```

**Cấu hình Vercel** (`vercel.json`):
- `buildCommand`: Build React frontend (`cd frontend && npm install && npm run build`)
- `outputDirectory`: `frontend/dist` (static files)
- `rewrites`: Route `/api/*` → `api/app.py` (Python serverless function)
- Database dùng `/tmp/story_creator.db` trên Vercel (read-only filesystem)

**Environment Variables** (Vercel Dashboard → Settings → Environment Variables):
- `OPENAI_API_KEY` — cho GPT features

## Testing

```bash
.venv\Scripts\python.exe api/test.py          # Core tests
.venv\Scripts\python.exe api/test_nosql.py    # NoSQL tests
.venv\Scripts\python.exe api/test_api_key.py  # API key validation
```

## Tech Stack

### Backend
- **Flask** 3.0 — Web framework
- **Flask-CORS** — Cross-origin support
- **Flasgger** — Swagger UI
- **TinyDB** — Lightweight NoSQL database
- **OpenAI** — GPT-4o-mini integration
- **python-dotenv** — Environment management

### Frontend
- **React** 18 — Component UI
- **Vite** 5 — Build tool
- **TailwindCSS** 3.4 + **DaisyUI** 4.6 — Styling
- **React Router** 6 — Client-side routing
- **Axios** — HTTP client

## Thuật toán liên kết câu chuyện

Câu chuyện được liên kết tự động khi chia sẻ:
1. **Nhân vật** — cùng entity xuất hiện ở nhiều câu chuyện
2. **Địa điểm** — cùng location
3. **Thời gian** — time cone gần nhau

Sử dụng inverted indices: `{entity_id: [story_ids]}` để tìm liên kết hiệu quả.

## Auto-World Generation

Khi tạo câu chuyện, thế giới tự động được chọn theo thể loại:
- Adventure → Fantasy World
- Mystery → Modern World
- Conflict → Historical World
- Discovery → Sci-Fi World

## GPT Simulation Mode

```bash
.venv\Scripts\python.exe api/main.py -i simulation
```

- Giả lập nhân vật trong câu chuyện
- 3 lựa chọn tại mỗi thời điểm: hành động / đối nghịch / rút lui
- Nhân vật không điều khiển do GPT quyết định
- Auto-translate ENG → VN

## Documentation

Xem thêm trong `docs/`:
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Architecture](docs/architecture_diagram.md)
- [Models Guide](docs/MODELS_GUIDE.md)
- [Storage Guide](docs/STORAGE_GUIDE.md)
- [GPT Integration](docs/GPT_INTEGRATION_GUIDE.md)
- [React Architecture](docs/REACT_ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT_GUIDE.md)
- [Quick Start](docs/QUICK_START.md)
- [Installation](docs/INSTALLATION.md)

## VS Code Tasks

Dự án cung cấp sẵn các tasks trong `.vscode/tasks.json`:
- `Run API Backend` — Flask API (port 5000)
- `Run React Frontend` — Vite dev server (port 3000)
- `Full Stack Dev` — Chạy cả hai
- `Run Tests` / `Run NoSQL Tests`
- `Build React` — Production build
- `Install Backend Deps` / `Install Frontend Deps`

## License

MIT
