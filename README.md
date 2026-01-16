# Story Creator

Dự án tạo thế giới và câu chuyện bằng Python với giao diện trực quan, database NoSQL, và tích hợp GPT-5 Mini cho mô phỏng nhân vật.

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

### 🎮 GPT-5 Mini Interactive Simulation Mode
- 🤖 **Tích hợp GPT-5 Mini** (Upgraded from GPT-4o) để tự động dịch thuật ENG→VN
- 💾 Lưu kết quả dịch thuật vào database và ánh xạ vào câu chuyện
- 👤 **Giả lập là nhân vật** trong câu chuyện
- 📚 Đọc câu chuyện của nhân vật một cách liên mạch theo thứ tự thời gian nón ánh sáng
- ⚔️ Lựa chọn hành động của nhân vật tại các thời điểm trong nón ánh sáng
  - 3 lựa chọn: 2 đối nghịch + 1 từ bỏ
- 🤖 Nhân vật không được giả lập sẽ được GPT-5 Mini lựa chọn tự động
- ⏱️ Mỗi nhân vật có tiến trình xử lý riêng và chung 1 dòng thời gian
- 🔮 Dự đoán tình huống xảy ra từ câu chuyện và sự liên kết của các nhân vật
- ⚡ **Hiệu suất tối ưu**: Model mới nhất với chất lượng cao và chi phí thấp

### User Interfaces
- 🖥️ Giao diện Terminal (TUI) trực quan
- 🎨 Giao diện đồ họa (GUI) với tkinter
- 🎮 **Giao diện Simulation (Interactive Character Mode)**

## Cài đặt

```bash
# Clone repository
git clone https://github.com/AI-Nhat-Phuc/story-creator.git
cd story-creator

# Cài đặt dependencies
pip install -r requirements.txt

# (Optional) Set OpenAI API key for GPT-5 Mini features
export OPENAI_API_KEY='your-api-key-here'
```

## Sử dụng

### Giao diện Terminal với NoSQL (Khuyến nghị - Hiệu suất cao)

```bash
python main.py -i terminal -s nosql
# hoặc đơn giản (NoSQL là mặc định)
python main.py
```

### 🎮 Chế độ Simulation (GPT-5 Mini Interactive)

```bash
# Requires OPENAI_API_KEY environment variable
python main.py -i simulation

# Or run the demo
python demo_gpt_simulation.py
```

### ⭐ Demo: Auto-Generate World from Story Genre

```bash
# Run the auto-generation demo
python demo_auto_world.py

# This will demonstrate:
# - Creating worlds automatically for each genre
# - Random configuration generation
# - Customizing world configuration
# - Dangerous creatures based on danger levels
```

### Giao diện GUI với NoSQL

```bash
python main.py -i gui -s nosql
```

### Sử dụng JSON files (legacy)

```bash
python main.py -i terminal -s json -d data/
python main.py -i gui -s json -d data/
```

### Chỉ định database file

```bash
python main.py -s nosql --db-path my_stories.db
```

## Cấu trúc dự án

```
story-creator/
├── models/              # Data models (World, Story, Location, Entity, TimeCone)
│   ├── __init__.py
│   ├── world.py
│   ├── story.py
│   ├── location.py
│   ├── entity.py
│   └── time_cone.py
├── generators/          # Generators for worlds and stories
│   ├── __init__.py
│   ├── world_generator.py
│   ├── story_generator.py
│   └── story_linker.py
├── utils/              # Utilities (Storage, etc.)
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
# Set API key
export OPENAI_API_KEY='sk-...'

# Start simulation mode
python main.py -i simulation

# Follow the prompts to:
# 1. Select a world
# 2. Choose your character
# 3. Enable/disable auto-translation
# 4. Make decisions at key moments
# 5. Watch the story unfold
```

### Demo Simulation

```bash
# Run full demo (works without API key in limited mode)
python demo_gpt_simulation.py
```

## Yêu cầu hệ thống

- Python 3.7 trở lên
- TinyDB >= 4.8.0 (cài tự động với pip install -r requirements.txt)
- OpenAI >= 1.0.0 (cho GPT-4 features)
- tkinter (thường đi kèm với Python, cho GUI)
- **OpenAI API Key** (cho simulation mode với GPT-4)

## License

MIT License

## Author

AI-Nhat-Phuc
