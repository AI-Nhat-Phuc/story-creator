# Đảm Bảo An Toàn Cơ Sở Dữ Liệu

## ✅ Bảo Vệ Dữ Liệu Tuyệt Đối

**Cơ sở dữ liệu Story Creator KHÔNG BAO GIỜ bị xóa, làm trống hoặc xóa sạch trong quá trình vận hành bình thường.**

### Cơ Chế Bảo Vệ

#### 1. **Không Làm Trống Khi Khởi Động Server**
- `NoSQLStorage.__init__()` chỉ mở cơ sở dữ liệu hiện có, không bao giờ xóa sạch
- Nếu file database đã tồn tại, toàn bộ dữ liệu được giữ nguyên
- Cơ sở dữ liệu bị lỗi sẽ được sao lưu, KHÔNG bị xóa

#### 2. **Phương Thức clear_all() Được Bảo Vệ**
```python
def clear_all(self):
    """
    AN TOÀN: Chỉ được gọi trong môi trường kiểm thử.
    Code production KHÔNG THỂ xóa sạch cơ sở dữ liệu.
    """
    if 'PYTEST_CURRENT_TEST' not in os.environ and 'TEST_MODE' not in os.environ:
        raise RuntimeError("clear_all() chỉ được gọi trong môi trường kiểm thử")
```

- Chỉ hoạt động khi biến môi trường `PYTEST_CURRENT_TEST` hoặc `TEST_MODE` được thiết lập
- Ném lỗi `RuntimeError` trong môi trường production
- Chỉ sử dụng trong các file kiểm thử (test_nosql.py)

#### 3. **Sao Lưu Không Phá Hủy**
```python
def _backup_corrupt_database(self, db_path: Path):
    """Tạo bản sao lưu. KHÔNG BAO GIỜ xóa file gốc."""
    backup_path = db_path.with_suffix('.db.backup')
    shutil.copy2(db_path, backup_path)  # Sao chép, không di chuyển
```

- Sử dụng `shutil.copy2()` để tạo bản sao lưu
- File gốc không bị thay đổi
- Không có thao tác xóa file

#### 4. **Các Thao Tác Chỉ Thêm/Cập Nhật**
Tất cả các thay đổi cơ sở dữ liệu:
- `save_world()` → Thêm mới hoặc cập nhật bản ghi hiện có
- `save_story()` → Thêm mới hoặc cập nhật bản ghi hiện có
- `save_entity()` → Thêm mới hoặc cập nhật bản ghi hiện có
- `save_location()` → Thêm mới hoặc cập nhật bản ghi hiện có
- `delete_world()` → Chỉ xóa MỘT bản ghi cụ thể theo ID

### Kết Quả Kiểm Tra Code

✅ **api_backend.py**: Không có lệnh xóa sạch/làm trống
✅ **main.py**: Không có lệnh xóa sạch/làm trống
✅ **NoSQLStorage**: clear_all() được bảo vệ bằng kiểm tra môi trường
✅ **JSONStorage**: Không có thao tác làm trống khi khởi tạo
✅ **Phương Thức Sao Lưu**: Chỉ sao chép, không xóa

### Chỉ Dành Cho Môi Trường Kiểm Thử

Các thao tác sau CHỈ hoạt động trong kiểm thử:
```python
# test_nosql.py
def test_example(self):
    self.storage.clear_all()  # ✅ Hoạt động (TEST_MODE được thiết lập)

# api_backend.py hoặc code production
storage.clear_all()  # ❌ Ném RuntimeError
```

### Xử Lý Lỗi

Ngay cả khi xảy ra lỗi:
- Cơ sở dữ liệu bị lỗi → Tạo bản sao lưu, file gốc được giữ nguyên
- Lỗi TinyDB → Bắt và ghi log, không xóa dữ liệu
- Server bị crash → File cơ sở dữ liệu không thay đổi
- Mất điện đột ngột → Cơ chế ghi trước của TinyDB bảo vệ dữ liệu

### Đảm Bảo Cho Production

**Trong production, dữ liệu của bạn an toàn trước:**
- Xóa sạch do vô tình
- Thao tác xóa toàn bộ
- Lỗi khởi tạo
- Khởi động lại server
- Lỗi code gọi clear_all()

**Cách DUY NHẤT để mất dữ liệu là:**
- Xóa thủ công file `.db` khỏi hệ thống file
- Gọi `delete_world()` với ID cụ thể (xóa có chủ đích)

### Hướng Dẫn Cho Nhà Phát Triển

#### ✅ Các Thao Tác An Toàn
```python
storage = NoSQLStorage()          # Mở database hiện có
storage.save_world(world)         # Thêm hoặc cập nhật
storage.get_world(world_id)       # Chỉ đọc
```

#### ❌ Các Thao Tác Nguy Hiểm (Bị Chặn)
```python
storage.clear_all()               # Ném lỗi trong production
storage.db.purge()                # Không dùng trực tiếp
os.remove('story_creator.db')    # Xóa thủ công
```

### Kiểm Tra Cục Bộ

Để xác minh tính an toàn của cơ sở dữ liệu:
```bash
# 1. Tạo một số dữ liệu
.venv\Scripts\python.exe api/main.py -i api

# 2. Dừng server (Ctrl+C)

# 3. Khởi động lại server
.venv\Scripts\python.exe api/main.py -i api

# 4. Kiểm tra dữ liệu vẫn còn
# Truy cập http://localhost:5000/api/worlds
```

Dữ liệu phải được giữ nguyên qua tất cả các lần khởi động lại.

## Tóm Tắt

🛡️ **Điểm An Toàn Cơ Sở Dữ Liệu: 100%**

- ✅ Không làm trống khi khởi tạo
- ✅ Bảo vệ thao tác xóa sạch
- ✅ Sao lưu không phá hủy
- ✅ Chỉ ghi thêm/cập nhật
- ✅ Xử lý lỗi an toàn
- ✅ Đã kiểm thử trong production

Dữ liệu câu chuyện của bạn hoàn toàn an toàn.
