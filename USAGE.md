# USAGE GUIDE - Story Creator

## Hướng dẫn sử dụng

### 1. Khởi chạy ứng dụng

#### Giao diện Terminal (TUI)
```bash
python main.py -i terminal
```

Hoặc đơn giản:
```bash
python main.py
```

#### Giao diện đồ họa (GUI)
```bash
python main.py -i gui
```

### 2. Chạy Demo

Để xem ví dụ đầy đủ về cách tạo thế giới và câu chuyện:

```bash
python demo.py
```

Demo sẽ:
- Tạo 1 thế giới Fantasy
- Tạo 3 địa điểm
- Tạo 3 thực thể
- Tạo 3 câu chuyện với các thể loại khác nhau
- Liên kết các câu chuyện với nhau
- Hiển thị đồ thị liên kết
- Xuất dữ liệu JSON vào thư mục `demo_data/`

### 3. Chạy Tests

Để kiểm tra tất cả chức năng hoạt động đúng:

```bash
python test.py
```

### 4. Sử dụng Terminal Interface

Khi khởi động Terminal Interface, bạn sẽ thấy menu chính:

```
------------------------------------------------------------
MENU CHÍNH
------------------------------------------------------------
1. Tạo thế giới mới
2. Xem danh sách thế giới
3. Chọn thế giới hiện tại
4. Tạo câu chuyện mới
5. Xem danh sách câu chuyện
6. Liên kết các câu chuyện
7. Xem chi tiết thế giới
0. Thoát
------------------------------------------------------------
```

#### 4.1. Tạo thế giới mới

1. Chọn option `1`
2. Chọn loại thế giới (1-4):
   - 1: Fantasy (Giả tưởng)
   - 2: Sci-Fi (Khoa học viễn tưởng)
   - 3: Modern (Hiện đại)
   - 4: Historical (Lịch sử)
3. Nhập mô tả thế giới
4. Nhập số lượng địa điểm (mặc định 3)
5. Nhập số lượng thực thể (mặc định 3)

Ví dụ:
```
Chọn loại: 1
Mô tả: Một thế giới ma thuật với các vương quốc và rồng
Số lượng địa điểm: 5
Số lượng thực thể: 4
```

#### 4.2. Tạo câu chuyện

1. Đảm bảo đã chọn thế giới hiện tại (option 3)
2. Chọn option `4`
3. Chọn thể loại (1-4):
   - 1: Adventure (Phiêu lưu)
   - 2: Mystery (Bí ẩn)
   - 3: Conflict (Xung đột)
   - 4: Discovery (Khám phá)
4. Nhập mô tả câu chuyện

Ví dụ:
```
Chọn thể loại: 1
Mô tả: Một hiệp sĩ trẻ bắt đầu cuộc hành trình tìm kiếm thanh kiếm huyền thoại
```

#### 4.3. Liên kết câu chuyện

1. Tạo ít nhất 2 câu chuyện trong cùng một thế giới
2. Chọn option `6`
3. Chọn phương thức liên kết:
   - 1: Theo thực thể chung
   - 2: Theo địa điểm chung
   - 3: Theo thời gian chung
   - 4: Tất cả các phương thức

### 5. Sử dụng GUI Interface

#### 5.1. Tab "Tạo thế giới"

1. Chọn loại thế giới (Fantasy, Sci-Fi, Modern, Historical)
2. Nhập mô tả thế giới vào ô text
3. Chọn số lượng địa điểm và thực thể
4. Click "Tạo thế giới"

#### 5.2. Tab "Tạo câu chuyện"

1. Chọn thế giới từ dropdown (hoặc click "Làm mới danh sách")
2. Chọn thể loại câu chuyện
3. Nhập mô tả câu chuyện
4. Click "Tạo câu chuyện"
5. Click "Liên kết các câu chuyện" để tự động liên kết

#### 5.3. Tab "Xem dữ liệu"

1. Xem danh sách tất cả thế giới
2. Click vào một thế giới để xem chi tiết
3. Xem danh sách câu chuyện của thế giới đó
4. Click "Làm mới" để cập nhật danh sách

### 6. Cấu trúc dữ liệu

Tất cả dữ liệu được lưu trong thư mục `data/` (hoặc thư mục bạn chỉ định):

```
data/
├── worlds/         # File JSON cho mỗi thế giới
├── stories/        # File JSON cho mỗi câu chuyện
├── locations/      # File JSON cho mỗi địa điểm
├── entities/       # File JSON cho mỗi thực thể
└── time_cones/     # File JSON cho mỗi time cone
```

Mỗi file JSON có tên là UUID của đối tượng.

### 7. Tùy chỉnh thư mục dữ liệu

```bash
python main.py -i terminal -d /path/to/custom/data
```

### 8. Làm việc với JSON files

Bạn có thể:
- Đọc và chỉnh sửa các file JSON trực tiếp
- Sao lưu thư mục `data/` để backup
- Chia sẻ các file JSON với người khác
- Import/Export data

### 9. Ví dụ workflow hoàn chỉnh

```bash
# 1. Chạy demo để tạo dữ liệu mẫu
python demo.py

# 2. Khám phá dữ liệu được tạo
ls -la demo_data/*/
cat demo_data/worlds/*.json

# 3. Khởi động terminal interface
python main.py -i terminal

# 4. Trong terminal:
#    - Chọn "2" để xem danh sách thế giới
#    - Chọn "3" để chọn một thế giới
#    - Chọn "4" để tạo thêm câu chuyện
#    - Chọn "6" để liên kết câu chuyện
#    - Chọn "7" để xem chi tiết
```

### 10. Troubleshooting

#### Lỗi: ModuleNotFoundError: No module named 'tkinter'

**Giải pháp**: 
- Trên Ubuntu/Debian: `sudo apt-get install python3-tk`
- Trên macOS: tkinter thường có sẵn
- Trên Windows: tkinter thường có sẵn
- Hoặc sử dụng Terminal Interface thay vì GUI: `python main.py -i terminal`

#### Không thể tạo file

**Giải pháp**: Đảm bảo bạn có quyền ghi vào thư mục hiện tại hoặc chỉ định thư mục khác:
```bash
python main.py -d ~/my-stories
```

#### Dữ liệu không được lưu

**Giải pháp**: Kiểm tra thư mục `data/` đã được tạo chưa. Chương trình sẽ tự động tạo nhưng cần quyền ghi.

### 11. Tips & Tricks

- Sử dụng mô tả chi tiết cho thế giới và câu chuyện để có kết quả tốt hơn
- Tạo nhiều câu chuyện trong cùng thế giới để thấy được sức mạnh của hệ thống liên kết
- Backup thư mục `data/` thường xuyên
- Sử dụng demo script để học cách sử dụng API

### 12. Advanced Usage

#### Sử dụng trong code Python

```python
from models import World, Story
from generators import WorldGenerator, StoryGenerator
from utils import Storage

# Khởi tạo
storage = Storage("my_data")
world_gen = WorldGenerator()
story_gen = StoryGenerator()

# Tạo thế giới
world = world_gen.generate(
    prompt="Your world description",
    world_type="fantasy"
)
storage.save_world(world.to_dict())

# Tạo câu chuyện
story = story_gen.generate(
    prompt="Your story description",
    world_id=world.world_id,
    genre="adventure"
)
storage.save_story(story.to_dict())
```

## Liên hệ & Đóng góp

Nếu bạn gặp vấn đề hoặc muốn đóng góp, vui lòng tạo issue trên GitHub repository.
