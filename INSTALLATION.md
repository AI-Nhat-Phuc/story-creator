# Hướng Dẫn Cài Đặt và Sử Dụng Story Creator

## 📋 Mục Lục

1. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
2. [Cài đặt](#cài-đặt)
3. [Cấu hình](#cấu-hình)
4. [Sử dụng cơ bản](#sử-dụng-cơ-bản)
5. [Sử dụng nâng cao](#sử-dụng-nâng-cao)
6. [Tính năng GPT-5 Mini](#tính-năng-gpt-5-mini)
7. [Xử lý sự cố](#xử-lý-sự-cố)

---

## 🖥️ Yêu Cầu Hệ Thống

### Tối thiểu
- **Python**: 3.7 hoặc cao hơn
- **RAM**: 512MB
- **Dung lượng**: 100MB

### Khuyến nghị
- **Python**: 3.9 hoặc cao hơn
- **RAM**: 1GB trở lên
- **Dung lượng**: 500MB

### Hệ điều hành hỗ trợ
- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu 18.04+, Debian, Fedora, etc.)

---

## 📦 Cài Đặt

### Bước 1: Cài đặt Python

#### Windows
1. Tải Python từ [python.org/downloads](https://www.python.org/downloads/)
2. Chạy file cài đặt
3. ✅ **Quan trọng**: Chọn "Add Python to PATH"
4. Click "Install Now"

Kiểm tra:
```bash
python --version
```

#### macOS
```bash
# Sử dụng Homebrew
brew install python3

# Hoặc tải từ python.org
```

Kiểm tra:
```bash
python3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

Kiểm tra:
```bash
python3 --version
```

### Bước 2: Clone Repository

```bash
# Clone từ GitHub
git clone https://github.com/AI-Nhat-Phuc/story-creator.git

# Di chuyển vào thư mục
cd story-creator
```

**Lưu ý**: Nếu chưa cài Git, tải từ [git-scm.com](https://git-scm.com/)

### Bước 3: Cài đặt Dependencies

```bash
# Cài đặt tất cả các thư viện cần thiết
pip install -r requirements.txt
```

**Windows**: Dùng `pip` thay vì `pip3`  
**macOS/Linux**: Có thể cần `pip3` hoặc `python3 -m pip`

### Bước 4: Xác nhận cài đặt

```bash
# Kiểm tra các thư viện đã cài
pip list | grep -E "tinydb|openai"

# Hoặc chạy test
python test.py
```

**Thành công** nếu thấy:
```
✅ ALL TESTS PASSED
```

---

## ⚙️ Cấu Hình

### Cấu hình cơ bản (Không cần GPT-5 Mini)

Không cần cấu hình gì thêm. Có thể sử dụng ngay!

### Cấu hình GPT-5 Mini (Tùy chọn - Upgraded từ GPT-4o)

#### Bước 1: Lấy API Key

1. Đăng ký tài khoản tại [platform.openai.com](https://platform.openai.com/)
2. Vào mục "API Keys"
3. Click "Create new secret key"
4. Copy API key (bắt đầu với `sk-...`)

#### Bước 2: Thiết lập API Key

**Windows (Command Prompt)**
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

**Windows (PowerShell)**
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

**macOS/Linux**
```bash
export OPENAI_API_KEY='sk-your-api-key-here'
```

**Lưu vĩnh viễn (macOS/Linux)**
```bash
# Thêm vào ~/.bashrc hoặc ~/.zshrc
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**Lưu vĩnh viễn (Windows)**
1. Mở "Environment Variables"
2. Thêm biến mới: `OPENAI_API_KEY`
3. Giá trị: `sk-your-api-key-here`

#### Bước 3: Kiểm tra

```bash
# Windows (Command Prompt)
echo %OPENAI_API_KEY%

# Windows (PowerShell)
echo $env:OPENAI_API_KEY

# macOS/Linux
echo $OPENAI_API_KEY
```

---

## 🚀 Sử Dụng Cơ Bản

### 1. Giao diện Terminal (Khuyến nghị cho người mới)

```bash
python main.py
```

**Hoặc**

```bash
python main.py -i terminal
```

#### Menu chính

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

#### Ví dụ: Tạo thế giới đầu tiên

1. Chọn `1` (Tạo thế giới mới)
2. Chọn loại thế giới:
   - `1`: Fantasy (Giả tưởng)
   - `2`: Sci-Fi (Khoa học viễn tưởng)
   - `3`: Modern (Hiện đại)
   - `4`: Historical (Lịch sử)
3. Nhập mô tả: `Một thế giới ma thuật với các vương quốc cổ xưa`
4. Nhập số lượng địa điểm: `5`
5. Nhập số lượng thực thể: `3`

**Kết quả**: Thế giới mới được tạo với 5 địa điểm và 3 nhân vật!

#### Ví dụ: Tạo câu chuyện

1. Chọn `3` (Chọn thế giới hiện tại)
2. Chọn thế giới vừa tạo
3. Chọn `4` (Tạo câu chuyện mới)
4. Chọn thể loại:
   - `1`: Adventure (Phiêu lưu)
   - `2`: Mystery (Bí ẩn)
   - `3`: Conflict (Xung đột)
   - `4`: Discovery (Khám phá)
5. Nhập mô tả: `Một hiệp sĩ trẻ bắt đầu hành trình`

**Kết quả**: Câu chuyện mới được tạo trong thế giới!

### 2. Giao diện GUI (Đồ họa)

```bash
python main.py -i gui
```

#### Tabs chính

1. **Tab "Tạo thế giới"**
   - Chọn loại thế giới
   - Nhập mô tả
   - Chọn số lượng địa điểm và thực thể
   - Click "Tạo thế giới"

2. **Tab "Tạo câu chuyện"**
   - Chọn thế giới
   - Chọn thể loại
   - Nhập mô tả
   - Click "Tạo câu chuyện"

3. **Tab "Xem dữ liệu"**
   - Xem danh sách thế giới
   - Xem chi tiết
   - Xem câu chuyện

### 3. Chạy Demo

```bash
# Demo cơ bản (JSON)
python demo.py

# Demo NoSQL
python demo_nosql.py

# Demo GPT-5 Mini (cần API key - model mới nhất, hiệu suất tối ưu)
python demo_gpt_simulation.py
```

---

## 🎯 Sử Dụng Nâng Cao

### Storage Options

#### NoSQL (Mặc định - Nhanh hơn)

```bash
# Sử dụng database mặc định
python main.py -s nosql

# Chỉ định database riêng
python main.py -s nosql --db-path my_stories.db
```

**Ưu điểm**:
- Truy vấn nhanh hơn 10-100 lần
- Một file dễ backup
- Hỗ trợ đồng thời

#### JSON Files (Legacy - Dễ đọc)

```bash
# Sử dụng JSON files
python main.py -s json -d my_data/
```

**Ưu điểm**:
- Dễ đọc và chỉnh sửa thủ công
- Không cần database

### Liên kết câu chuyện

```bash
# Trong Terminal Interface
# Chọn option 6: "Liên kết các câu chuyện"
```

Chọn phương thức:
1. Theo thực thể chung (nhân vật)
2. Theo địa điểm chung
3. Theo thời gian chung
4. Tất cả các phương thức

### Export và Import

#### Export thế giới

```bash
# NoSQL
cp story_creator.db backup_$(date +%Y%m%d).db

# JSON
tar -czf backup_$(date +%Y%m%d).tar.gz data/
```

#### Import thế giới

```bash
# NoSQL
cp backup_20260116.db story_creator.db

# JSON
tar -xzf backup_20260116.tar.gz
```

---

## 🤖 Tính Năng GPT-5 Mini

**⚡ Mới**: Đã nâng cấp lên GPT-5 Mini (2025-08-07) - Model mới nhất với hiệu suất tối ưu, chất lượng cao và chi phí thấp!

### Cài đặt và cấu hình

1. **Cài đặt API Key** (xem phần [Cấu hình](#cấu-hình))

2. **Kiểm tra kết nối**
```bash
python -c "import os; print('API Key:', os.getenv('OPENAI_API_KEY')[:10] + '...')"
```

### Chế độ Simulation (Mô phỏng nhân vật)

```bash
python main.py -i simulation
```

#### Luồng hoạt động

1. **Chọn thế giới**
   - Hiển thị danh sách thế giới
   - Chọn số thứ tự

2. **Chọn nhân vật điều khiển**
   - Hiển thị danh sách nhân vật
   - Chọn nhân vật bạn muốn điều khiển
   - Hoặc chọn "Watch all" để xem AI điều khiển tất cả

3. **Kích hoạt tính năng**
   - Auto-translation (ENG→VN): `y` hoặc `n`

4. **Bắt đầu simulation**
   - Mỗi thời điểm, nhận 3 lựa chọn:
     - **A**: Hành động chính
     - **B**: Hành động đối nghịch
     - **C**: Từ bỏ/Rút lui

5. **Xem kết quả**
   - Câu chuyện của mỗi nhân vật theo timeline
   - Có bản dịch tiếng Việt (nếu bật)

#### Ví dụ Simulation

```
⏰ Time Index: 0
------------------------------------------------------------

🎮 Warrior's turn:
   Situation: Time 0: Warrior faces a new challenge.
   (Tiếng Việt: Thời điểm 0: Chiến binh đối mặt thử thách mới.)

   Choices:
   A. Attack the enemy directly
   B. Retreat and plan strategy
   C. Abandon the quest

   Your choice (A/B/C): A
   ✅ You chose: Attack the enemy directly

🤖 Wizard chose: B - Retreat and plan strategy
```

### Auto-translation

Tất cả văn bản tự động dịch sang tiếng Việt và lưu trong database:

```python
# Tự động dịch
"The warrior faces a difficult choice"
→ "Chiến binh đối mặt lựa chọn khó khăn"
```

### AI Decision Making

Nhân vật không điều khiển sẽ có GPT-5 Mini quyết định dựa trên:
- Tính cách nhân vật
- Thuộc tính (Strength, Intelligence, etc.)
- Ngữ cảnh câu chuyện

---

## 🔧 Xử Lý Sự Cố

### Lỗi: ModuleNotFoundError

**Lỗi**: `ModuleNotFoundError: No module named 'tinydb'`

**Giải pháp**:
```bash
pip install tinydb openai
```

### Lỗi: OpenAI API

**Lỗi**: `OpenAI API key required`

**Giải pháp**:
```bash
# Thiết lập API key
export OPENAI_API_KEY='sk-your-key'

# Hoặc chạy không cần GPT-5 Mini
python main.py -i terminal  # Không simulation
```

### Lỗi: tkinter not found

**Lỗi**: `ModuleNotFoundError: No module named 'tkinter'`

**Giải pháp Ubuntu/Debian**:
```bash
sudo apt-get install python3-tk
```

**Giải pháp macOS**:
```bash
# Thường đã có sẵn, nếu không:
brew install python-tk
```

**Workaround**: Dùng Terminal thay vì GUI
```bash
python main.py -i terminal
```

### Database bị khóa

**Lỗi**: `database is locked`

**Giải pháp**:
```bash
# Đóng tất cả instances đang chạy
# Hoặc dùng database mới
python main.py --db-path new_database.db
```

### Performance chậm

**Triệu chứng**: Chương trình chạy chậm

**Giải pháp**:
```bash
# Chuyển sang NoSQL nếu đang dùng JSON
python main.py -s nosql

# Giảm số lượng entities/locations khi tạo
# Chọn 3 thay vì 10
```

### GPT-5 Mini timeout

**Lỗi**: `Request timeout`

**Giải pháp**:
1. Kiểm tra kết nối internet
2. GPT-5 Mini thường nhanh hơn, nhưng nếu timeout vẫn xảy ra:
3. Thử lại sau vài phút
4. Chạy demo không cần GPT:
```bash
python main.py -i terminal
```

---

## 📚 Tài Liệu Tham Khảo

### Files quan trọng

- `README.md` - Tổng quan dự án
- `USAGE.md` - Hướng dẫn sử dụng chi tiết
- `instructions.md` - Context cho developers
- `requirements.txt` - Dependencies

### Commands hữu ích

```bash
# Xem version
python --version

# Xem help
python main.py --help

# Chạy tests
python test.py
python test_nosql.py

# Xem database stats
python -c "from utils import NoSQLStorage; s=NoSQLStorage(); print(s.get_stats())"
```

### Cấu trúc dữ liệu

```
data/                    # JSON storage (nếu dùng -s json)
├── worlds/
├── stories/
├── locations/
├── entities/
└── time_cones/

story_creator.db         # NoSQL database (mặc định)
```

---

## 💡 Tips & Tricks

### 1. Backup thường xuyên

```bash
# Backup NoSQL
cp story_creator.db backup.db

# Backup JSON
cp -r data/ backup_data/
```

### 2. Sử dụng mô tả chi tiết

```
# ❌ Không tốt
"Thế giới ma thuật"

# ✅ Tốt
"Một thế giới ma thuật với các vương quốc cổ xưa, rồng huyền thoại, và các pháp sư quyền năng"
```

### 3. Tạo nhiều câu chuyện

Tạo ít nhất 3-5 câu chuyện trong cùng thế giới để thấy được sức mạnh của hệ thống liên kết.

### 4. Thử nghiệm simulation

```bash
# Tạo dữ liệu mẫu trước
python demo_nosql.py

# Sau đó chạy simulation
python main.py -i simulation
```

### 5. Sử dụng custom database cho mỗi project

```bash
python main.py --db-path project_a.db
python main.py --db-path project_b.db
```

---

## 🆘 Hỗ Trợ

### Báo lỗi

Nếu gặp lỗi, cung cấp:
1. Hệ điều hành
2. Python version (`python --version`)
3. Error message đầy đủ
4. Các bước tái hiện lỗi

### GitHub Issues

[github.com/AI-Nhat-Phuc/story-creator/issues](https://github.com/AI-Nhat-Phuc/story-creator/issues)

---

## 📝 Checklist Bắt Đầu

- [ ] Cài đặt Python 3.7+
- [ ] Clone repository
- [ ] Cài đặt dependencies (`pip install -r requirements.txt`)
- [ ] Chạy test để kiểm tra (`python test.py`)
- [ ] Chạy demo (`python demo.py`)
- [ ] Thử Terminal interface (`python main.py`)
- [ ] (Tùy chọn) Thiết lập OpenAI API key
- [ ] (Tùy chọn) Thử simulation mode (`python main.py -i simulation`)
- [ ] Tạo thế giới đầu tiên
- [ ] Tạo câu chuyện đầu tiên
- [ ] Liên kết câu chuyện
- [ ] Backup dữ liệu

---

**Chúc bạn sáng tạo thành công! 🎉**

*Cập nhật lần cuối: 2026-01-16*
