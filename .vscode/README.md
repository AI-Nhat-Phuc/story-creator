# VSCode Configuration for Story Creator

Thư mục này chứa các file cấu hình cho Visual Studio Code để có thể chạy và debug project dễ dàng mà không cần dùng terminal.

## 📁 Files

### `tasks.json` - Task Configurations
Chứa các task có thể chạy nhanh từ VSCode.

**Cách sử dụng:**
1. Press `Ctrl+Shift+P` (Windows/Linux) hoặc `Cmd+Shift+P` (macOS)
2. Gõ "Tasks: Run Task"
3. Chọn task muốn chạy

**Hoặc:**
- Press `Ctrl+Shift+B` để chạy default build task (Terminal Interface)

**Available Tasks:**

#### 🚀 Run Application
- **🚀 Run Terminal Interface** - Chạy giao diện terminal (Default: Ctrl+Shift+B)
- **🎨 Run GUI Interface** - Chạy giao diện đồ họa
- **🎮 Run Simulation Mode** - Chạy chế độ simulation (cần API key)
- **🗄️ Run with NoSQL Storage** - Chạy với NoSQL database
- **📄 Run with JSON Storage** - Chạy với JSON files

#### 🎬 Demos
- **🎬 Run Basic Demo** - Demo cơ bản
- **🎬 Run NoSQL Demo** - Demo NoSQL storage
- **🎬 Run GPT-4 Simulation Demo** - Demo GPT-4 simulation

#### ✅ Tests
- **✅ Run All Tests** - Chạy test.py
- **✅ Run NoSQL Tests** - Chạy test_nosql.py
- **✅ Run All Tests (Complete)** - Chạy tất cả tests

#### 🔧 Utilities
- **📦 Install Dependencies** - Cài đặt requirements.txt
- **🔍 Check Python Version** - Kiểm tra Python version
- **📋 List Installed Packages** - Xem packages đã cài
- **🗑️ Clean Database Files** - Xóa database files
- **🗑️ Clean JSON Data** - Xóa JSON data directory

#### ❓ Help
- **❓ Show Help** - Hiển thị help message
- **📖 Open README** - Mở README.md
- **📖 Open Installation Guide** - Mở INSTALLATION.md

### `launch.json` - Debug Configurations
Chứa các cấu hình để debug code.

**Cách sử dụng:**
1. Mở file Python muốn debug
2. Set breakpoint (click vào số dòng)
3. Press `F5` hoặc click "Run and Debug" icon
4. Chọn configuration muốn dùng

**Hoặc:**
- Press `Ctrl+F5` để run without debugging

**Available Configurations:**

#### 🚀 Run/Debug
- **🚀 Run Terminal Interface** - Debug terminal interface
- **🎨 Run GUI Interface** - Debug GUI
- **🎮 Run Simulation Mode** - Debug simulation (với API key)
- **🗄️ Run with NoSQL Storage** - Debug với NoSQL
- **📄 Run with JSON Storage** - Debug với JSON

#### 🎬 Demos
- **🎬 Debug Basic Demo** - Debug demo.py
- **🎬 Debug NoSQL Demo** - Debug demo_nosql.py
- **🎬 Debug GPT-4 Simulation Demo** - Debug demo_gpt_simulation.py

#### ✅ Tests
- **✅ Debug All Tests** - Debug test.py
- **✅ Debug NoSQL Tests** - Debug test_nosql.py

#### 🔧 Debug Current File
- **🔧 Debug Current File** - Debug file đang mở
- **🔧 Debug Current File (No JustMyCode)** - Debug kể cả thư viện

### `settings.json` - Project Settings
Cấu hình chung cho project trong VSCode.

**Bao gồm:**
- Python interpreter settings
- Auto-save configuration
- File encoding (UTF-8)
- Tab size và spaces
- Files to exclude from search
- Git settings
- Markdown preview settings

## 🎯 Quick Start

### 1. Mở Project trong VSCode
```bash
code .
```

### 2. Chạy Terminal Interface
**Option A:** Using Task
- Press `Ctrl+Shift+B`

**Option B:** Using Debug
- Press `F5`
- Chọn "🚀 Run Terminal Interface"

### 3. Chạy GUI
**Using Task:**
- Press `Ctrl+Shift+P`
- Gõ "Tasks: Run Task"
- Chọn "🎨 Run GUI Interface"

**Using Debug:**
- Press `F5`
- Chọn "🎨 Run GUI Interface"

### 4. Chạy Simulation Mode
**Lưu ý:** Cần set OPENAI_API_KEY trước

**Windows:**
```cmd
set OPENAI_API_KEY=sk-your-key
```

**Linux/macOS:**
```bash
export OPENAI_API_KEY=sk-your-key
```

**Sau đó:**
- Press `Ctrl+Shift+P`
- Chọn "Tasks: Run Task"
- Chọn "🎮 Run Simulation Mode"

## 🔧 Customization

### Thêm Task mới

Edit `.vscode/tasks.json`:

```json
{
    "label": "Your Task Name",
    "type": "shell",
    "command": "python",
    "args": ["script.py"],
    "problemMatcher": []
}
```

### Thêm Debug Configuration

Edit `.vscode/launch.json`:

```json
{
    "name": "Your Config Name",
    "type": "python",
    "request": "launch",
    "program": "${workspaceFolder}/your_script.py",
    "console": "integratedTerminal"
}
```

### Thay đổi Default Task

Trong `tasks.json`, tìm task muốn set làm default và thêm:

```json
"group": {
    "kind": "build",
    "isDefault": true
}
```

## 📝 Tips

### Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| Run Task | `Ctrl+Shift+B` | `Cmd+Shift+B` |
| Run Any Task | `Ctrl+Shift+P` → Tasks | `Cmd+Shift+P` → Tasks |
| Debug | `F5` | `F5` |
| Run without Debug | `Ctrl+F5` | `Cmd+F5` |
| Stop | `Shift+F5` | `Shift+F5` |
| Restart | `Ctrl+Shift+F5` | `Cmd+Shift+F5` |
| Command Palette | `Ctrl+Shift+P` | `Cmd+Shift+P` |

### Debug Tips

1. **Set Breakpoint**: Click vào số dòng
2. **Conditional Breakpoint**: Right-click số dòng → Add Conditional Breakpoint
3. **Watch Variables**: Thêm biến vào Watch panel
4. **Debug Console**: Gõ Python expressions trong debug
5. **Call Stack**: Xem function call history

### Task Tips

1. **Run Multiple Tasks**: Sử dụng `dependsOn` trong task
2. **Auto-run on Save**: Thêm task vào workspace settings
3. **Custom Variables**: Dùng `${workspaceFolder}`, `${file}`, etc.

## 🆘 Troubleshooting

### Task không chạy

**Giải pháp:**
1. Kiểm tra Python đã cài đúng: `python --version`
2. Kiểm tra trong PATH
3. Thử restart VSCode

### Debug không hoạt động

**Giải pháp:**
1. Cài Python extension cho VSCode
2. Select Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Kiểm tra file `launch.json` syntax

### API Key không nhận

**Giải pháp:**
1. Set trong terminal trước khi mở VSCode
2. Hoặc thêm vào `launch.json`:
```json
"env": {
    "OPENAI_API_KEY": "sk-your-key-here"
}
```

### Terminal không hiển thị tiếng Việt

**Giải pháp:**
1. Thêm vào settings.json:
```json
"terminal.integrated.fontFamily": "Consolas, 'Courier New', monospace"
```
2. Hoặc cài font hỗ trợ Vietnamese

## 📚 Resources

- [VSCode Tasks Documentation](https://code.visualstudio.com/docs/editor/tasks)
- [VSCode Debugging](https://code.visualstudio.com/docs/editor/debugging)
- [Python in VSCode](https://code.visualstudio.com/docs/python/python-tutorial)

---

**Cập nhật:** 2026-01-16
