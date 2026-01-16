# Story Creator

Dự án tạo thế giới và câu chuyện bằng Python với giao diện trực quan và database NoSQL.

## Tính năng

- ✨ Tạo thế giới (worlds) theo các thể loại: Fantasy, Sci-Fi, Modern, Historical
- 📖 Tạo câu chuyện (stories) với nhiều thể loại khác nhau
- 📍 Quản lý địa điểm (locations) trong thế giới
- 👥 Quản lý thực thể (entities) tham gia vào câu chuyện
- ⏰ Quản lý thời gian theo nón ánh sáng (time cones)
- 🔗 Liên kết các câu chuyện với nhau theo thực thể, địa điểm, và thời gian
- 💾 Lưu trữ dữ liệu: **NoSQL Database (TinyDB)** hoặc JSON files
- ⚡ **Hiệu suất cao** với NoSQL database (mặc định)
- 🖥️ Giao diện Terminal (TUI) trực quan
- 🎨 Giao diện đồ họa (GUI) với tkinter

## Cài đặt

```bash
# Clone repository
git clone https://github.com/AI-Nhat-Phuc/story-creator.git
cd story-creator

# Cài đặt dependencies
pip install -r requirements.txt
```

## Sử dụng

### Giao diện Terminal với NoSQL (Khuyến nghị - Hiệu suất cao)

```bash
python main.py -i terminal -s nosql
# hoặc đơn giản (NoSQL là mặc định)
python main.py
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

## Yêu cầu hệ thống

- Python 3.7 trở lên
- TinyDB >= 4.8.0 (cài tự động với pip install -r requirements.txt)
- tkinter (thường đi kèm với Python, cho GUI)

## License

MIT License

## Author

AI-Nhat-Phuc
