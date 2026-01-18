# Story Creator

Hệ thống tạo thế giới và câu chuyện tương tác với **React Frontend + Flask API Backend**, database NoSQL, và tích hợp GPT-4o-mini cho mô phỏng nhân vật.

## Tính năng

### Core Features
- ✨ Tạo thế giới (worlds) theo các thể loại: Fantasy, Sci-Fi, Modern, Historical
- 📖 Tạo câu chuyện (stories) với nhiều thể loại khác nhau
- 📍 Quản lý địa điểm (locations) trong thế giới
- 👥 Quản lý thực thể (entities) tham gia vào câu chuyện
- ⏰ Quản lý thời gian theo nón ánh sáng (time cones)
- 🔗 Liên kết các câu chuyện với nhau theo thực thể, địa điểm, và thời gian
- 💾 Lưu trữ dữ liệu: **NoSQL Database (TinyDB)** hoặc JSON files
- ⚡ **Hiệu suất cao** với NoSQL database (mặc định)

### ⭐ NEW: Auto-Generate World from Story Genre
- 🌍 **Tự động tạo thế giới** khi chọn thể loại câu chuyện
- 🎲 **Cấu hình ngẫu nhiên** có thể chỉnh sửa:
  - Số lượng người (3-15, ngẫu nhiên)
  - Có rừng hay không (ngẫu nhiên 70% có)
  - Số lượng sông (0-5, ngẫu nhiên)
  - Số lượng hồ (0-3, ngẫu nhiên)
  - Mức độ nguy hiểm của sông/rừng/hồ (0-10, ngẫu nhiên)
- 👹 **Sinh vật nguy hiểm** tự động tạo dựa trên mức độ nguy hiểm
  - Càng nguy hiểm → càng nhiều sinh vật nguy hiểm
  - Mỗi 3 điểm danger = 1 sinh vật
  - Thuộc tính động dựa trên mức độ nguy hiểm
- 🎯 **Genre-based World Type Mapping**:
  - Adventure → Fantasy World
  - Mystery → Modern World
  - Conflict → Historical World
  - Discovery → Sci-Fi World

### 🎮 GPT-5 Nano Interactive Simulation Mode
- 🤖 **Tích hợp GPT-5 Nano** - Model nhỏ gọn, hiệu quả nhất
- 💾 Lưu kết quả dịch thuật vào database và ánh xạ vào câu chuyện
- 👤 **Giả lập là nhân vật** trong câu chuyện
- 📚 Đọc câu chuyện của nhân vật một cách liên mạch theo thứ tự thời gian nón ánh sáng
- ⚔️ Lựa chọn hành động của nhân vật tại các thời điểm trong nón ánh sáng
  - 3 lựa chọn: 2 đối nghịch + 1 từ bỏ
- 🤖 Nhân vật không được giả lập sẽ được GPT-4o Mini lựa chọn tự động
- ⏱️ Mỗi nhân vật có tiến trình xử lý riêng và chung 1 dòng thời gian
- 🔮 Dự đoán tình huống xảy ra từ câu chuyện và sự liên kết của các nhân vật
- ✅ **Modal xác nhận** khi sử dụng GPT (không còn checkbox)
- 🔗 **Sơ đồ quan hệ**: Hiển thị mối quan hệ giữa các nhân vật

### User Interfaces

**⚛️ React Web Application (Default)**
- 🌟 **React 18** với TailwindCSS + DaisyUI
- 🎨 Responsive, modern UI/UX
- 🔄 Real-time updates với REST API
- 📊 Dashboard với thống kê
- 🌍 Quản lý thế giới với GPT analysis
- 📖 Quản lý câu chuyện với auto-character detection
- 🔗 Visualize relationships giữa nhân vật
- 📚 **Swagger UI** - Interactive API documentation

**🎮 Simulation Interface**
- Interactive character mode với GPT decision-making
- Terminal-based character control
- Run: `python main.py -i simulation`

**📦 Legacy (Archived in `legacy/`)**
- Flask templates web interface
- Tkinter GUI
- Demo scripts

## Quick Start

### 🚀 React + API Mode (Recommended)

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt
npm install                        # Install concurrently
cd frontend && npm install && cd ..

# 2. Chạy cả frontend và backend
npm run dev

# Hoặc chạy riêng từng phần:
# Terminal 1 (activate venv trước):
.venv\Scripts\Activate.ps1        # Windows PowerShell
python main.py -i api

# Terminal 2:
cd frontend && npm run dev
```

**Truy cập:**
- Frontend: http://localhost:3000
- API Swagger: http://localhost:5000/api/docs
- API Root: http://localhost:5000/ (auto-redirect to Swagger)

### 📚 Chi tiết

Xem [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) và [docs/REACT_ARCHITECTURE.md](docs/REACT_ARCHITECTURE.md)

## Sử dụng

### API Backend Mode (for React)

```bash
python main.py -i api              # API server on port 5000 with Swagger UI
python main.py -i api --debug      # With debug mode
```

### Legacy Web Interface

```bash
python main.py -i web              # Flask templates (deprecated)
```

### Simulation Mode

```bash
python main.py -i simulation       # Character simulation with GPT
```

## Cấu trúc dự án

```
story-creator/
├── frontend/            # ⚛️ React application
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── pages/      # Page components
│   │   ├── services/   # API client
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── interfaces/         # Backend interfaces
│   ├── api_backend.py  # ✨ Pure REST API (NEW)
│   ├── web_interface.py # Flask templates (legacy)
│   └── simulation_interface.py
│
├── services/           # Business logic layer
│   ├── gpt_service.py
│   └── character_service.py
│
├── core/
│   └── models/        # Data models
│       ├── world.py
│       ├── story.py
│       ├── location.py
│       ├── entity.py
│       └── time_cone.py
│
├── generators/        # Content generators
│   ├── world_generator.py
│   ├── story_generator.py
│   └── story_linker.py
│
├── storage/          # Storage backends
│   ├── nosql_storage.py  # TinyDB (default)
│   └── json_storage.py   # File-based (legacy)
│
├── ai/               # AI integration
│   ├── gpt_client.py
│   └── prompts.py
│
├── main.py          # Entry point
├── package.json     # Root npm scripts
└── requirements.txt # Python dependencies
```
│   ├── __init__.py
│   └── storage.py
├── interfaces/         # User interfaces
│   ├── __init__.py
│   ├── terminal_interface.py
│   └── gui_interface.py
├── data/               # Data storage (auto-created)
│   ├── worlds/
│   ├── stories/
│   ├── locations/
│   ├── entities/
│   └── time_cones/
├── main.py            # Main entry point
└── README.md
```

## Cấu trúc dữ liệu JSON

### World (Thế giới)

```json
{
  "type": "world",
  "world_id": "uuid",
  "name": "Tên thế giới",
  "description": "Mô tả thế giới",
  "created_at": "timestamp",
  "metadata": {
    "world_type": "fantasy",
    "themes": ["magic", "dragons"]
  },
  "stories": ["story_id_1", "story_id_2"],
  "locations": ["location_id_1", "location_id_2"],
  "entities": ["entity_id_1", "entity_id_2"]
}
```

### Story (Câu chuyện)

```json
{
  "type": "story",
  "story_id": "uuid",
  "title": "Tiêu đề câu chuyện",
  "content": "Nội dung câu chuyện",
  "world_id": "world_id",
  "created_at": "timestamp",
  "metadata": {
    "genre": "adventure"
  },
  "locations": ["location_id_1"],
  "entities": ["entity_id_1"],
  "time_cones": ["time_cone_id_1"],
  "linked_stories": ["story_id_2", "story_id_3"]
}
```

### Location (Địa điểm)

```json
{
  "type": "location",
  "location_id": "uuid",
  "name": "Tên địa điểm",
  "description": "Mô tả địa điểm",
  "world_id": "world_id",
  "created_at": "timestamp",
  "coordinates": {
    "x": 100.5,
    "y": 200.3,
    "z": 50.0
  },
  "metadata": {}
}
```

### Entity (Thực thể)

```json
{
  "type": "entity",
  "entity_id": "uuid",
  "name": "Tên thực thể",
  "entity_type": "character",
  "description": "Mô tả thực thể",
  "world_id": "world_id",
  "created_at": "timestamp",
  "attributes": {
    "strength": 8,
    "intelligence": 9
  },
  "relationships": [
    {
      "entity_id": "other_entity_id",
      "relationship_type": "friend"
    }
  ],
  "metadata": {}
}
```

### Time Cone (Nón ánh sáng thời gian)

```json
{
  "type": "time_cone",
  "time_cone_id": "uuid",
  "name": "Tên time cone",
  "description": "Mô tả ngữ cảnh thời gian",
  "world_id": "world_id",
  "created_at": "timestamp",
  "start_time": "Thời điểm bắt đầu",
  "end_time": "Thời điểm kết thúc",
  "reference_event": "Sự kiện tham chiếu",
  "metadata": {}
}
```

## Ví dụ sử dụng

### 1. Tạo thế giới Fantasy

```
Chọn loại thế giới: Fantasy
Mô tả: Một thế giới ma thuật với các vương quốc và rồng
Số địa điểm: 5
Số thực thể: 3
```

### 2. Tạo câu chuyện

```
Chọn thể loại: Adventure
Mô tả: Một hiệp sĩ trẻ bắt đầu cuộc hành trình tìm kiếm thanh kiếm huyền thoại
```

### 3. Liên kết câu chuyện

```
Phương thức: Theo thực thể chung
Kết quả: Các câu chuyện có cùng nhân vật sẽ được liên kết với nhau
```

## Thuật toán liên kết câu chuyện

Hệ thống sử dụng các thuật toán logic để liên kết các câu chuyện:

1. **Liên kết theo thực thể**: Câu chuyện có chung nhân vật/đối tượng
2. **Liên kết theo địa điểm**: Câu chuyện diễn ra ở cùng vị trí
3. **Liên kết theo thời gian**: Câu chuyện có cùng ngữ cảnh thời gian (time cone)

## NoSQL Database vs JSON Files

### ⚡ NoSQL Database (TinyDB) - Mặc định

**Ưu điểm:**
- Truy vấn nhanh hơn với indexing
- Lọc và tìm kiếm hiệu quả
- Một file database duy nhất (dễ backup)
- Hỗ trợ ACID transactions
- Tốt hơn cho datasets lớn
- Hỗ trợ concurrent access

**Performance:**
- Query speed: ~0.0008s cho filtered queries
- Write speed: ~0.07s cho 100 records
- Load speed: ~0.003s cho 10 records

### 📄 JSON Files - Legacy

**Ưu điểm:**
- Dễ đọc và chỉnh sửa thủ công
- Không cần dependencies
- Phân tán theo thư mục
- Human-readable format

**Sử dụng khi:**
- Cần xem/sửa dữ liệu trực tiếp
- Dataset nhỏ (<100 records)
- Không quan tâm performance

## 🎮 GPT-4 Simulation Mode Features

### Interactive Character Simulation

Chế độ simulation cho phép bạn:

1. **Tự động dịch thuật (ENG→VN)**
   - GPT-4 tự động dịch tất cả văn bản từ Tiếng Anh sang Tiếng Việt
   - Kết quả dịch được lưu vào database
   - Ánh xạ vào câu chuyện đã tạo và sắp tạo

2. **Giả lập nhân vật**
   - Chọn một nhân vật để điều khiển
   - Đọc câu chuyện theo góc nhìn của nhân vật đó
   - Thứ tự theo nón ánh sáng thời gian (light cone chronology)

3. **Lựa chọn tương tác**
   - Tại mỗi thời điểm quan trọng, chọn hành động cho nhân vật
   - 3 lựa chọn được tạo tự động:
     - **A**: Hành động chính
     - **B**: Hành động đối nghịch
     - **C**: Từ bỏ/Rút lui

4. **AI điều khiển nhân vật phụ**
   - Nhân vật không được điều khiển sẽ có GPT-4 quyết định
   - Dựa trên tính cách và thuộc tính của nhân vật

5. **Timeline riêng biệt**
   - Mỗi nhân vật có tiến trình xử lý riêng
   - Tất cả chia sẻ một dòng thời gian chung
   - Đồng bộ hóa qua global time index

6. **Dự đoán tình huống**
   - GPT-4 dự đoán tình huống tiếp theo
   - Dựa trên câu chuyện và quyết định của các nhân vật
   - Liên kết logic giữa các sự kiện

### Ví dụ Sử dụng

```bash
# Story Creator

Story Creator is an interactive world and story generation platform with a modern React frontend, Flask REST API backend, and GPT-4o-mini AI integration. Build, link, and simulate fictional worlds, stories, characters, and locations with high performance and a clean service architecture.

## Features
- 🌍 Create and manage worlds (fantasy, sci-fi, modern, historical)
- 📖 Write and link stories with auto-detected characters and locations
- 🗺️ Visualize timelines, maps, and character relationships
- 🤖 GPT-4o-mini integration for world/story/character generation
- 🧑‍💻 React 18 + TailwindCSS + DaisyUI frontend
- 🚀 Fast NoSQL (TinyDB) or JSON storage
- 🧩 Modular service layer for business logic

## Quick Start
1. Clone the repo & install Python/Node.js dependencies
2. (Optional) Add your OpenAI API key to `.env`
3. Run `npm run dev` for full stack, or see [docs/INSTALLATION.md](docs/INSTALLATION.md)
4. Access UI at http://localhost:3000, API docs at http://localhost:5000/api/docs

## Documentation
- See [docs/](docs/) for architecture, API, models, storage, and more
- For Copilot/service/frontend coding rules, see [.github/copilot-instructions.md](.github/copilot-instructions.md)
AI-Nhat-Phuc
