# Quick Start Guide - Story Creator

## 1. Requirements
- Python 3.7+ (recommend 3.11+)
- Node.js 18+

## 2. Install Dependencies
```bash
# Python
python -m venv .venv
.venv/Scripts/activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Node.js (frontend)
cd frontend
npm install
cd ..
```

## 3. (Optional) Add GPT API Key
Create a `.env` file in the project root:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 4. Run the App
```bash
# Full stack (recommended)

# Or run backend and frontend separately:
python main.py -i api
cd frontend && npm run dev
```

## 5. Access
- React UI: http://localhost:3000
- API Swagger: http://localhost:5000/api/docs
### Tạo Story

1. Click **"Tạo Nhanh"** → **"Tạo Câu Chuyện"**
2. Chọn **World** từ dropdown
3. Chọn **Genre**: Adventure, Mystery, Conflict, Discovery
4. Nhập **Description**: Nội dung câu chuyện (mention character names)
5. Chỉnh **Time Index** slider (vị trí trong timeline)
6. Click **"Tạo Câu Chuyện"**

### Xem World Details

1. Click vào world name trong danh sách
2. Xem tabs:
   - **Stories**: Tất cả stories theo timeline
   - **Characters**: Danh sách nhân vật
   - **Locations**: Danh sách địa điểm
   - **Statistics**: Thống kê world

## Features Chính

### 🌍 Auto World Generation
- Tự động tạo entities và locations dựa trên world type
- GPT analysis tạo entities phù hợp với description
- Random generation nếu không dùng GPT

### 📖 Smart Story Creation
- Auto-detect characters được nhắc đến trong story
- Link stories với characters tự động
- Time-based organization (0-100 timeline)

### 🤖 GPT Integration
- Analyze world description → extract entities/locations
- Character simulation (simulation mode)
- English → Vietnamese translation

### 📊 Statistics & Visualization
- Real-time stats dashboard
- Character relationship diagrams
- Story timeline view

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Save (in forms) |
| Esc | Close modals |
| F5 | Refresh page |
| F12 | Open DevTools |

## Tips & Tricks

### Character Detection

Nhắc đến character trong story description:
```
"Arthur và Merlin đi đến lâu đài"
→ Auto-detect: Arthur, Merlin
→ Auto-link vào story
```

### GPT World Analysis

Mô tả chi tiết để GPT tạo entities tốt hơn:
```
✅ Good: "A medieval kingdom ruled by King Arthur,
         with the wizard Merlin as advisor..."

❌ Bad: "A fantasy world"
```

### Time Index

- **0-20**: Beginning/Origin stories
- **20-50**: Early/Mid development
- **50-80**: Major events
- **80-100**: Current/End times

## Command Line Options

```bash
# Web interface (default)
python main.py -i web

# Debug mode (xem logs chi tiết)
python main.py -i web --debug

# Custom port
python main.py -i web --port 8080

# Simulation mode
python main.py -i simulation

# Specify storage
python main.py -i web -s nosql    # Default, fast
python main.py -i web -s json     # Legacy, slow
```

## VS Code Tasks

Sử dụng tasks có sẵn trong VS Code:

1. Press `Ctrl+Shift+P`
2. Type "Run Task"
3. Chọn:
   - 🚀 Run Web Interface
   - 🎮 Run Simulation Mode
   - ✅ Run All Tests
   - 🗑️ Clean Database Files

## Troubleshooting

### Port 5000 đang được sử dụng

**Auto fix**: Server tự động kill process cũ

**Manual fix**:
```powershell
# Tìm process
netstat -ano | findstr :5000

# Kill process (replace PID)
taskkill /PID 12345 /F

# Hoặc dùng port khác
python main.py -i web --port 8080
```

### GPT không hoạt động

1. Check `.env` file tồn tại
2. Check API key format: `sk-proj-...`
3. Test với: `python test_api_key.py`
4. Check internet connection

### Database errors

```powershell
# Clear database
del story_creator.db

# Restart application
python main.py -i web
```

### Import errors

```powershell
# Check virtual environment active
# Should see (.venv) in prompt

# Activate if not
.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

## Common Workflows

### Workflow 1: Quick Story Creation

1. Create world without GPT (fast)
2. Create 3-5 stories
3. View world details
4. Check character relationships

### Workflow 2: GPT-Enhanced World

1. Write detailed world description
2. Use GPT analysis (wait ~5s)
3. Review generated entities/locations
4. Create stories mentioning characters
5. View relationship diagram

### Workflow 3: Story Series

1. Create world
2. Create first story (time_index=10)
3. Create sequel (time_index=20, mention same characters)
4. Create prequel (time_index=5)
5. View timeline in chronological order

## Data Files

### NoSQL Database (Default)
```
story_creator.db          # Single database file
demo_nosql.db            # Demo database
test.db                  # Test database
```

### JSON Files (Legacy)
```
data/
  ├── worlds/
  ├── stories/
  ├── entities/
  ├── locations/
  └── time_cones/
```

### Backup

```powershell
# Backup database
copy story_creator.db backup_$(Get-Date -Format yyyyMMdd_HHmmss).db

# Restore
copy backup_20260118_143000.db story_creator.db
```

## Next Steps

### Beginner
1. ✅ Complete quick start
2. 📖 Read [WEB_INTERFACE_GUIDE.md](WEB_INTERFACE_GUIDE.md)
3. 🎮 Try creating 5 stories
4. 📊 Explore statistics dashboard

### Intermediate
1. 📖 Read [GPT_INTEGRATION_GUIDE.md](GPT_INTEGRATION_GUIDE.md)
2. 🤖 Set up GPT API
3. 🎮 Try simulation mode
4. 🔗 Explore story linking

### Advanced
1. 📖 Read [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
2. 🔧 Customize world types
3. 🧪 Write tests
4. 🚀 Deploy application

## Support

### Documentation
- `README.md` - Project overview
- `INSTALLATION.md` - Detailed setup
- `USAGE.md` - Detailed usage
- `docs/` - Technical guides

### Testing
- `test.py` - Core functionality tests
- `test_nosql.py` - Storage tests
- `test_api_key.py` - GPT validation

### Demos
- `demo.py` - Basic demo
- `demo_nosql.py` - NoSQL demo
- `demo_gpt_simulation.py` - GPT demo
- `demo_auto_world.py` - Auto-generation demo

## Keyboard Reference

### Browser (Web Interface)

| Key | Action |
|-----|--------|
| F12 | Open DevTools |
| Ctrl+Shift+I | Inspect Element |
| Ctrl+R | Refresh |
| Ctrl+Shift+Delete | Clear Cache |

### VS Code

| Key | Action |
|-----|--------|
| Ctrl+` | Toggle Terminal |
| Ctrl+B | Toggle Sidebar |
| Ctrl+P | Quick Open File |
| Ctrl+Shift+P | Command Palette |
| F5 | Start Debugging |

## Cheat Sheet

```bash
# Start web interface
python main.py -i web

# Open in browser
http://127.0.0.1:5000

# Create world
1. Click "Tạo Thế Giới"
2. Fill form → Submit

# Create story
1. Click "Tạo Câu Chuyện"
2. Select world → Fill form → Submit

# View world
Click world name → See tabs

# Stats
Dashboard → View all stats

# Test
python test.py

# Clean database
del *.db

# Backup
copy story_creator.db backup.db
```

Chúc bạn sử dụng Story Creator vui vẻ! 🎉
