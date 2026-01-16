# Story Creator - AI Agent Instructions

## Project Overview
Interactive storytelling system that generates interconnected fictional worlds, stories, characters, and locations. Features GPT-4 integration for character simulation and auto-translation (ENG→VN).

## Architecture

### Core Domain Models (`models/`)
- **World**: Container for stories, locations, entities. Has metadata including world_type (fantasy/sci-fi/modern/historical)
- **Story**: Narrative content with genre, linked to entities/locations via ID lists
- **Entity**: Characters with attributes (Strength, Intelligence, Charisma) and entity_type
- **Location**: Physical places with coordinates (x, y)
- **TimeCone**: Temporal context binding stories to timeline indices

All models follow pattern: `to_dict()`, `to_json()`, `from_dict()`, `from_json()` for serialization.

### Storage Layer (`utils/`)
**Dual storage backends** - default is NoSQL for performance:
- **NoSQLStorage** (`nosql_storage.py`): TinyDB-based, single file database with separate tables (worlds, stories, locations, entities, time_cones). Use `Query()` for filtering.
- **Storage** (`storage.py`): File-based JSON storage, legacy option, keeps separate directories per model type.

**Critical**: Always specify storage type via `--storage` or `-s` flag. NoSQL is default and 10-100x faster for queries.

### Generators (`generators/`)
- **WorldGenerator**: Creates worlds from prompts, auto-generates locations/entities based on world_type templates
- **StoryGenerator**: Generates stories with genre-specific templates (adventure/mystery/conflict/discovery)
- **StoryLinker**: Links stories by shared entities, locations, or time using graph algorithms

### Interfaces (`interfaces/`)
- **terminal_interface.py**: Menu-driven TUI (default)
- **gui_interface.py**: Tkinter-based GUI with tabs for world/story creation
- **simulation_interface.py**: Interactive character mode with GPT-4 decision-making

## GPT-4 Integration (`utils/gpt_integration.py`)

**Environment Setup**: Requires `OPENAI_API_KEY` in `.env` file (use `python-dotenv` to load)

Key methods:
- `translate_eng_to_vn(text)`: Auto-translation for simulation mode
- `generate_character_decision(character_name, situation, story_context, character_traits)`: AI decides character actions based on personality

**Model**: Uses `gpt-4-turbo-preview` (referenced as GPT-4.1 in docs)

## Development Workflow

### Environment Setup
```powershell
# Use virtual environment Python (CRITICAL)
.venv/Scripts/python.exe <script.py>

# Install packages
pip install -r requirements.txt
pip install python-dotenv  # For .env support
```

### Running the Application
```bash
# Terminal interface with NoSQL (recommended)
python main.py -i terminal -s nosql

# Simulation mode (requires API key)
python main.py -i simulation

# GUI interface
python main.py -i gui
```

### Testing
```bash
# Core functionality tests
python test.py

# NoSQL-specific tests
python test_nosql.py

# API key validation
python test_api_key.py
```

### Demos
- `demo.py`: Basic JSON workflow (creates demo_data/)
- `demo_nosql.py`: NoSQL performance showcase (creates demo_nosql.db)
- `demo_gpt_simulation.py`: GPT-4 character simulation
- `demo_auto_world.py`: Auto-world generation from story genre

## Key Patterns & Conventions

### Story Linking Algorithm
Stories are linked when they share:
1. **Entities** (characters appearing in multiple stories)
2. **Locations** (same place, different stories)
3. **Time Cones** (temporal proximity)

Implementation uses inverted indices: `{entity_id: [story_ids]}` to efficiently find shared elements.

### Auto-World Generation
Genre-to-world-type mapping (in `generators/world_generator.py`):
- Adventure → Fantasy
- Mystery → Modern
- Conflict → Historical
- Discovery → Sci-Fi

Randomized configuration includes:
- Number of people (3-15)
- Forests (70% chance)
- Rivers (0-5), Lakes (0-3)
- Danger levels (0-10) determine creature spawning (1 creature per 3 danger points)

### Simulation Mode Flow
1. User selects world
2. Choose character to control (or watch AI-controlled)
3. At each time index, get 3 choices: A (action), B (opposite), C (abandon)
4. Non-controlled characters use GPT-4 for decisions
5. Auto-translate results if enabled
6. Progress saved to database with timeline tracking

### Database Schema (NoSQL)
Tables: `worlds`, `stories`, `locations`, `entities`, `time_cones`

**Query pattern**:
```python
from tinydb import Query
WorldQuery = Query()
self.worlds.search(WorldQuery.world_id == world_id)
```

**Update vs Insert**: Always check existence first, then update or insert.

## Critical Files for Understanding

- `main.py`: Entry point, argument parsing, interface routing
- `generators/story_linker.py`: Core linking logic with graph algorithms
- `utils/nosql_storage.py`: Performance-critical storage layer
- `interfaces/simulation_interface.py`: Complex GPT-4 interaction flow
- `models/world.py`: Base model pattern used by all domain objects

## Common Tasks

### Add New World Type
1. Update `WORLD_TYPES` dict in `generators/world_generator.py`
2. Add themes, location_types, entity_types lists
3. No other changes needed - generator handles the rest

### Add New Story Genre
1. Update `STORY_GENRES` in `generators/story_generator.py`
2. Add templates for that genre
3. Optionally update genre-to-world mapping in `demo_auto_world.py`

### Add New Model Field
1. Update `__init__()` in model class
2. Add to `to_dict()` serialization
3. Add to `from_dict()` deserialization
4. Update both storage backends (`save_*` and `load_*` methods)

### Debugging Storage Issues
- NoSQL: Use `db.purge()` to clear tables, or delete `.db` file
- JSON: Clear directories in `data/` or `demo_data/`
- Check `get_stats()` for counts

## VS Code Configuration

**launch.json**: All configurations use `.venv/Scripts/python.exe` explicitly

**tasks.json**: Available tasks with emoji prefixes (🚀 Run, 🎬 Demo, ✅ Test, 🗑️ Clean)

**Python environment**: Auto-configured virtual environment at `.venv/`

## Translation & Localization
- UI: Vietnamese (Tiếng Việt)
- Code: English comments/docstrings
- GPT responses: English → Auto-translate to Vietnamese when enabled
- Database stores both English and Vietnamese text when translation is active

## Error Handling Patterns
- GPT errors: Catch `Exception`, return descriptive error messages
- Storage errors: Check existence before operations
- User input: Validate in interface layer, not in models/generators
- API quota: Test with `test_api_key.py` before running simulations

## Performance Considerations
- Use NoSQL storage for datasets >50 items
- Story linking is O(n×m) where n=stories, m=avg entities per story
- GPT calls are blocking - simulate one character at a time
- TinyDB is thread-safe but not optimized for concurrent writes
