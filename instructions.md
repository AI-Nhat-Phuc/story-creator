# Story Creator - Project Instructions & Context

## Project Overview

Story Creator là một hệ thống tạo thế giới và câu chuyện bằng Python với khả năng mô phỏng nhân vật tương tác sử dụng GPT-4.

### Mục đích dự án
- Tạo thế giới (worlds) và câu chuyện (stories) từ prompts
- Liên kết các câu chuyện trong cùng một thế giới
- Mô phỏng nhân vật với AI
- Lưu trữ hiệu quả với NoSQL database
- Hỗ trợ dịch thuật tự động ENG→VN

## Architecture

### Core Components

#### 1. Data Models (`models/`)
- **World**: Thế giới chứa nhiều câu chuyện
- **Story**: Câu chuyện trong thế giới
- **Location**: Địa điểm diễn ra sự kiện
- **Entity**: Thực thể (nhân vật, vật thể)
- **TimeCone**: Nón ánh sáng thời gian (temporal context)

**Đặc điểm:**
- UUID-based identification
- JSON serialization/deserialization
- Bidirectional linking
- Vietnamese UTF-8 support

#### 2. Generators (`generators/`)
- **WorldGenerator**: Tạo thế giới từ prompts
  - 4 loại: fantasy, sci-fi, modern, historical
  - Tự động tạo locations và entities
  
- **StoryGenerator**: Tạo câu chuyện từ prompts
  - 4 thể loại: adventure, mystery, conflict, discovery
  - Tự động tạo time cones
  
- **StoryLinker**: Liên kết câu chuyện
  - Theo entities chung
  - Theo locations chung
  - Theo time cones chung

#### 3. Storage Backends (`utils/`)
- **NoSQLStorage** (TinyDB): Mặc định, hiệu suất cao
  - Single-file database
  - Indexed queries
  - 10-100x faster than JSON
  - CRUD operations với Query support
  
- **Storage** (JSON): Legacy, human-readable
  - File-per-entity
  - Organized directory structure
  - Direct file editing support

#### 4. GPT-4 Integration (`utils/`)
- **GPTIntegration**: Wrapper cho OpenAI API
  - Auto-translation (ENG→VN)
  - Character decision generation
  - Situation prediction
  - Dynamic choice generation
  
- **SimulationState**: Quản lý state mô phỏng
  - Character timelines
  - Translation storage
  - Global time management
  
- **CharacterTimeline**: Timeline riêng cho mỗi nhân vật
  - Chronological events
  - Player vs AI control
  - Light cone time ordering

#### 5. Interfaces (`interfaces/`)
- **TerminalInterface**: TUI với menu tiếng Việt
- **GUIInterface**: Tkinter GUI với tabs
- **SimulationInterface**: Interactive character simulation
  - Player character selection
  - Decision making (3 choices)
  - AI-controlled NPCs
  - Story viewing by character

## Key Features

### 1. World & Story Creation
```python
# Tạo thế giới
world_gen = WorldGenerator()
world = world_gen.generate("Magical world", "fantasy")

# Tạo locations và entities
locations = world_gen.generate_locations(world, count=5)
entities = world_gen.generate_entities(world, count=3)

# Tạo câu chuyện
story_gen = StoryGenerator()
story = story_gen.generate(
    "Hero's journey",
    world_id=world.world_id,
    genre="adventure"
)
```

### 2. Story Linking
```python
# Liên kết theo nhiều tiêu chí
linker = StoryLinker()
linker.link_stories(
    stories,
    link_by_entities=True,
    link_by_locations=True,
    link_by_time=True
)
```

### 3. Character Simulation
```python
# Khởi tạo simulation
sim = SimulationState(world_id, story_ids)

# Thêm nhân vật
sim.add_character(entity_id, name, player_controlled=True)

# Tạo situation
event = sim.create_situation(entity_id, situation, context)

# Ghi quyết định
sim.record_decision(entity_id, event_id, "A", choice_text)
```

### 4. GPT-4 Features
```python
# Translation
gpt = GPTIntegration(api_key)
translated = gpt.translate_eng_to_vn("English text")

# Character decisions
decision = gpt.generate_character_decision(
    character_name,
    situation,
    context,
    traits
)

# Situation prediction
prediction = gpt.predict_next_situation(
    story,
    character_states,
    recent_decisions
)
```

## Storage Schema

### NoSQL Tables (TinyDB)
- `worlds`: World documents
- `stories`: Story documents
- `locations`: Location documents
- `entities`: Entity documents
- `time_cones`: TimeCone documents

### JSON Structure
```
data/
├── worlds/
│   └── {world_id}.json
├── stories/
│   └── {story_id}.json
├── locations/
│   └── {location_id}.json
├── entities/
│   └── {entity_id}.json
└── time_cones/
    └── {time_cone_id}.json
```

## Usage Patterns

### CLI Interface
```bash
# Terminal (default)
python main.py

# GUI
python main.py -i gui

# Simulation mode
python main.py -i simulation

# Specify storage
python main.py -s nosql --db-path custom.db
python main.py -s json -d data/
```

### Demo Scripts
```bash
# JSON demo
python demo.py

# NoSQL demo
python demo_nosql.py

# GPT simulation demo
python demo_gpt_simulation.py
```

## Development Guidelines

### Adding New Features

1. **Data Models**: Extend in `models/`
   - Add to_dict() và from_dict()
   - Add to_json() và from_json()
   - Support Vietnamese UTF-8

2. **Generators**: Add to `generators/`
   - Follow prompt-based pattern
   - Return model instances
   - Support metadata

3. **Storage**: Update both backends
   - NoSQLStorage: Add table và queries
   - Storage: Add save/load methods

4. **Interfaces**: Update relevant UIs
   - Terminal: Add menu options
   - GUI: Add tabs/widgets
   - Simulation: Add interactive features

### Code Style
- Python 3.7+ compatibility
- Type hints cho function signatures
- Docstrings cho all public methods
- Vietnamese support (UTF-8)
- Clean imports (no unused)

### Testing
```bash
# Run all tests
python test.py
python test_nosql.py

# Test specific features
python demo.py
python demo_nosql.py
python demo_gpt_simulation.py
```

## Environment Variables

### Required for GPT-4 Features
```bash
export OPENAI_API_KEY='sk-...'
```

### Optional
```bash
# Custom database path
export STORY_DB_PATH='path/to/db.db'

# Custom data directory (JSON)
export STORY_DATA_DIR='path/to/data'
```

## Dependencies

### Core
- Python >= 3.7
- tinydb >= 4.8.0 (NoSQL storage)
- openai >= 1.0.0 (GPT-4 integration)

### Optional
- tkinter (GUI, usually included with Python)

### Installation
```bash
pip install -r requirements.txt
```

## Performance Considerations

### NoSQL vs JSON
| Operation | NoSQL | JSON |
|-----------|-------|------|
| Query all (100) | 0.0002s | 0.01s+ |
| Filtered query | 0.0008s | 0.05s+ |
| Load single | 0.0003s | 0.001s+ |
| Write single | 0.0007s | 0.002s+ |

### Recommendations
- **NoSQL**: Production, large datasets (>100 records)
- **JSON**: Development, small datasets, manual editing

## Common Tasks

### Create a Complete World
1. Generate world with WorldGenerator
2. Generate locations (3-10)
3. Generate entities (3-10)
4. Save to storage
5. Generate stories (1-5)
6. Link stories with StoryLinker
7. Save all to storage

### Run Character Simulation
1. Load world with stories
2. Initialize SimulationState
3. Add characters from entities
4. Set player-controlled character
5. Start simulation loop
6. Handle decisions (player/AI)
7. Advance timeline
8. Show character stories

### Add Translation
1. Set OPENAI_API_KEY
2. Initialize GPTIntegration
3. Translate text with translate_eng_to_vn()
4. Store in SimulationState
5. Map to stories/situations
6. Display in UI

## Troubleshooting

### Common Issues

**ModuleNotFoundError: tinydb**
```bash
pip install tinydb
```

**OpenAI API Error**
```bash
# Check API key
echo $OPENAI_API_KEY

# Set if not set
export OPENAI_API_KEY='your-key'
```

**GUI not working**
```bash
# Install tkinter (Ubuntu/Debian)
sudo apt-get install python3-tk

# Or use terminal interface
python main.py -i terminal
```

**Database locked**
```bash
# Close other instances
# Or use new database
python main.py --db-path new.db
```

## Project Structure Summary

```
story-creator/
├── models/              # Data models (5 files)
├── generators/          # World/Story generators (3 files)
├── utils/              # Storage & GPT integration (4 files)
├── interfaces/         # Terminal/GUI/Simulation (3 files)
├── main.py             # Entry point
├── demo*.py            # Demo scripts (3 files)
├── test*.py            # Test suites (2 files)
├── requirements.txt    # Dependencies
├── README.md           # User documentation
├── USAGE.md            # Usage guide
└── instructions.md     # This file
```

## Future Enhancement Ideas

- [ ] Multi-language support (not just VN)
- [ ] Export stories to PDF/HTML
- [ ] Visual timeline viewer
- [ ] Character relationship graphs
- [ ] Story branching visualization
- [ ] Collaborative multi-player simulation
- [ ] Voice narration integration
- [ ] Image generation for scenes
- [ ] Save/load simulation snapshots
- [ ] Story quality metrics

## Version History

- **v1.0** (Initial): Core models, generators, JSON storage
- **v1.1** (NoSQL): Added TinyDB NoSQL storage backend
- **v1.2** (GPT-4): Added GPT-4 integration for simulation
  - Auto-translation
  - Character simulation
  - Interactive decision making
  - AI-controlled NPCs
  - Situation prediction

## Contact & Support

For issues or questions:
- GitHub Issues: AI-Nhat-Phuc/story-creator
- Email: (Add contact email if available)

---

**Last Updated**: 2026-01-16
**Maintained by**: AI-Nhat-Phuc
