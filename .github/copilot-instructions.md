# Story Creator - AI Agent Instructions

## Project Overview
Interactive storytelling system that generates interconnected fictional worlds, stories, characters, and locations. Features GPT-4o-mini integration for character simulation and content generation with clean service layer architecture.

## Architecture

### Service Layer (`services/`) **NEW**
**Business logic separated from UI** - Services handle all complex operations:
- **GPTService** (`gpt_service.py`): GPT operations with threading and callbacks
  - `generate_world_description()`: Async world description generation
  - `generate_story_description()`: Async story description with character context
  - `is_available()`: Check GPT availability
- **CharacterService** (`character_service.py`): Character management utilities (static methods)
  - `detect_mentioned_characters()`: Find mentioned characters in text
  - `get_character_names()`: Extract names with dangerous creature filtering
  - `format_character_display()`: Format as "👤 Name (type)"
  - `add_character_info_to_description()`: Append character info section

**Pattern**: Services use callback pattern for async operations, GUI never touches business logic directly.

### Core Domain Models (`models/`)
- **World**: Container for stories, locations, entities. Has metadata including world_type (fantasy/sci-fi/modern/historical)
- **Story**: Narrative content with genre, linked to entities/locations via ID lists
- **Entity**: Characters with attributes (Strength, Intelligence, Charisma) and entity_type
- **Location**: Physical places with coordinates (x, y)
- **TimeCone**: Temporal context binding stories to timeline indices

All models follow pattern: `to_dict()`, `to_json()`, `from_dict()`, `from_json()` for serialization.

### Storage Layer (`storage/`)
**Dual storage backends** - default is NoSQL for performance:
- **NoSQLStorage** (`nosql_storage.py`): TinyDB-based, single file database with separate tables (worlds, stories, locations, entities, time_cones). Use `Query()` for filtering.
- **JSONStorage** (`json_storage.py`): File-based JSON storage, legacy option, keeps separate directories per model type.

**Critical**: Always specify storage type via `--storage` or `-s` flag. NoSQL is default and 10-100x faster for queries.

### Generators (`generators/`)
- **WorldGenerator**: Creates worlds from prompts, auto-generates locations/entities based on world_type templates
- **StoryGenerator**: Generates stories with genre-specific templates (adventure/mystery/conflict/discovery)
- **StoryLinker**: Links stories by shared entities, locations, or time using graph algorithms

### Interfaces (`interfaces/`)
- **api_backend.py**: Pure REST API backend (DEFAULT) with Swagger documentation:
  - **Tech Stack**: Flask 3.0 + Flask-CORS + Flasgger (Swagger)
  - **Features**:
    - OpenAPI 2.0 compliant REST API
    - Swagger UI at `/api/docs` for interactive documentation
    - Auto-redirect from `/` and `/api` to Swagger UI
    - CORS enabled for React frontend (localhost:3000)
    - Async GPT integration with task-based results
    - Real-time world/story creation with GPT analysis
    - Character auto-detection from story descriptions
  - **API Endpoints** (all documented with OpenAPI specs):
    - `GET /` - Redirect to Swagger UI
    - `GET /api` - Redirect to Swagger UI
    - `GET /api/docs` - Swagger UI interface
    - `GET /api/health` - Health check
    - `GET/POST /api/worlds` - List and create worlds
    - `GET /api/worlds/<id>` - World details with related data
    - `POST /api/stories` - Create stories with auto-linking
    - `GET /api/worlds/<id>/characters` - List characters (excludes dangerous creatures)
    - `POST /api/gpt/analyze` - Async GPT world analysis with task tracking
    - `GET /api/gpt/results/<task_id>` - Poll GPT analysis results
    - `GET /api/stats` - System statistics
    - `GET /api/worlds/<id>/relationships` - Character relationship graph data

- **simulation_interface.py**: Interactive character mode with GPT decision-making (terminal-based)

**Note**: React frontend (`frontend/`) consumes the API. Legacy Flask templates web interface archived in `legacy/`.

## GPT Integration (`utils/gpt_integration.py` + `services/gpt_service.py`)

**Environment Setup**: Requires `OPENAI_API_KEY` in `.env` file (uses `python-dotenv` to load)

**Model**: Uses `gpt-4o-mini` (changed from gpt-5-nano due to reasoning tokens issue)

Key methods in GPTIntegration:
- `translate_eng_to_vn(text)`: Auto-translation for simulation mode
- `generate_character_decision(character_name, situation, story_context, character_traits)`: AI decides character actions based on personality

**Service Layer Usage** (PREFERRED):
```python
# Initialize service
self.gpt_service = GPTService(self.gpt)

# Generate with callbacks
self.gpt_service.generate_world_description(
    world_type="fantasy",
    callback_success=self._on_success,
    callback_error=self._on_error
)
```

**API Parameters**:
- Use `max_completion_tokens` instead of `max_tokens`
- Temperature parameter not supported (uses default value 1)
- Modal confirmation dialog before GPT calls in GUI

## Technologies & Dependencies

### Core Dependencies (requirements.txt)
- **Flask** (>=3.0.0): Web framework for HTTP server and routing
- **TinyDB** (>=4.8.0): Lightweight NoSQL database with zero configuration
- **psutil** (>=5.9.0): Cross-platform process management for server control
- **OpenAI** (>=1.0.0): GPT-4o-mini API integration for AI features
- **python-dotenv** (>=0.19.0): Environment variable management for API keys

### Frontend Technologies (React App)
- **React** (18.2.0): Modern component-based UI framework
- **React Router** (6.20.0): Client-side routing
- **Axios** (1.6.2): HTTP client for API calls
- **Vite** (5.0.8): Fast build tool and dev server
- **TailwindCSS** (3.4.1): Utility-first CSS framework
- **DaisyUI** (4.6.0): Component library built on Tailwind
- **PostCSS** (8.4.32): CSS processing
- **Autoprefixer** (10.4.16): CSS vendor prefixing

### Standard Library Modules
- `json`, `uuid`, `datetime`, `pathlib`, `typing`, `argparse`, `random`, `threading`, `signal`

**Minimum Python Version**: 3.7+

**Browser Compatibility**: Modern browsers with ES6 support (Chrome, Firefox, Edge, Safari)

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
# Full stack (React + API) - RECOMMENDED
npm run dev

# API backend only (for React)
python main.py -i api              # Default, runs on port 5000
python main.py -i api --debug      # With debug mode

# Simulation mode (requires API key)
python main.py -i simulation
python main.py -i simulation --world-id <id> --character-id <id>

# React frontend only
cd frontend && npm run dev         # Runs on port 3000
```

**Access:**
- React UI: http://localhost:3000
- API Swagger: http://localhost:5000/api/docs
- API Root: http://localhost:5000 (auto-redirects to Swagger)

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

### Web Interface Architecture
**Frontend-Backend Communication Pattern**:
- Frontend: Pure HTML/CSS/JavaScript (no framework) with TailwindCSS + DaisyUI components
- Backend: Flask REST API with JSON responses
- GPT Integration: Async task-based system to prevent UI blocking

**Key UI Components**:
1. **World Creation Form** (`createWorldForm`):
   - World type selection (fantasy/sci-fi/modern/historical)
   - Description textarea with GPT analysis button
   - Name input (required when using GPT)
   - Real-time character counter

2. **Story Creation Form** (`createStoryForm`):
   - World selection dropdown (loads dynamically)
   - Genre selection
   - Time index slider (0-100)
   - Description textarea with auto-character detection
   - Character pills showing detected characters

3. **World Details View**:
   - Tabs: Stories, Characters, Locations, Statistics
   - Story timeline view with time_index grouping
   - Character relationship diagram (SVG-based)
   - Location map visualization

**GPT Analysis Workflow**:
```javascript
// Client initiates analysis
POST /api/gpt/analyze { world_description, world_type }
→ Returns { task_id }

// Poll for results (500ms intervals)
GET /api/gpt/results/<task_id>
→ Returns { status: 'pending'|'completed'|'error', result }

// On completion, submit world with entities
POST /api/worlds { name, description, world_type, gpt_entities }
```

**Validation Rules**:
- World name is REQUIRED when using GPT analysis
- Story description auto-detects mentioned characters
- Dangerous creatures excluded from character selection
- Time index defaults to 0 if not specified

**Auto Server Management**:
- Uses `psutil` to detect processes on port 5000
- Terminates existing Flask servers before starting
- Waits 500ms for port to be released
- Falls back to manual termination message if auto-kill fails
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
- `interfaces/web_interface.py`: Flask-based web server with all API endpoints
- `templates/index.html`: Main web interface with TailwindCSS + DaisyUI
- `static/js/app.js`: Frontend JavaScript logic for dynamic UI updates
- `generators/story_linker.py`: Core linking logic with graph algorithms
- `storage/nosql_storage.py`: Performance-critical storage layer (TinyDB)
- `storage/json_storage.py`: Legacy file-based storage
- `interfaces/simulation_interface.py`: Complex GPT-4 interaction flow
- `core/models/world.py`: Base model pattern used by all domain objects
- `ai/gpt_client.py`: OpenAI GPT-4o-mini integration
- `services/gpt_service.py`: Async GPT service with callback pattern
- `services/character_service.py`: Character detection and formatting utilities

## Common Tasks

### Add New API Endpoint (Web Interface)
1. Add route decorator in `web_interface.py` within `_register_routes()`:
   ```python
   @self.app.route('/api/your-endpoint', methods=['GET', 'POST'])
   def your_endpoint():
       # Implementation
       return jsonify(result)
   ```
2. Add corresponding JavaScript function in `static/js/app.js`
3. Update UI components in `templates/index.html` to call the new endpoint
4. Test with browser DevTools Network tab

### Add New World Type
1. Update `WORLD_TYPES` dict in `generators/world_generator.py`
2. Add themes, location_types, entity_types lists
3. Add option in web interface dropdown (`templates/index.html`)
4. No other changes needed - generator handles the rest

### Add New Story Genre
1. Update `STORY_GENRES` in `generators/story_generator.py`
2. Add templates for that genre
3. Update genre dropdown in `templates/index.html`
4. Optionally update genre-to-world mapping in `demo_auto_world.py`

### Add New Model Field
1. Update `__init__()` in model class
2. Add to `to_dict()` serialization
3. Add to `from_dict()` deserialization
4. Update both storage backends (`save_*` and `load_*` methods)

### Debugging Storage Issues
- NoSQL: Use `db.purge()` to clear tables, or delete `.db` file
- JSON: Clear directories in `data/` or `demo_data/`
- Check `get_stats()` for counts

### Debugging Web Interface Issues
- Check browser console (F12) for JavaScript errors
- Monitor Network tab for API request/response details
- Enable debug mode: `python main.py -i web --debug` for Flask debug logs
- Check Flask console output for server-side errors
- Use `curl` or Postman to test API endpoints directly
- Verify GPT task IDs are stored correctly in session
- Check that port 5000 is available or use custom port with `--port`

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


## Copilot Coding Guidelines (Service & Frontend)

### Service Layer (Python)
- All business logic must be in `services/` (never in Flask routes or UI)
- Use callback pattern for async operations (see `GPTService`)
- Service methods should be stateless and reusable
- Never import or reference Flask, React, or any UI code in services
- Always catch exceptions and return error info via callback or return value
- Use `to_dict()`/`from_dict()` for all model objects
- Write service logic so it can be tested without running the web server
- Use `Service` suffix (e.g., `CharacterService`, `GPTService`)
- Add clear docstrings for all public methods

### Frontend (React)
- Use `services/api.js` for all HTTP requests (never call fetch/axios directly in components)
- UI logic in components (JSX, state, events); data logic in hooks or service files
- Use TailwindCSS utility classes and DaisyUI for UI
- Never use inline styles except for dynamic layout/animation
- Use React hooks (`useState`, `useEffect`, etc.) and context for global state
- Extract repeated UI into components (e.g., `GptButton`), use props for customization
- Use semantic HTML tags and add `aria-` attributes for accessibility
- Write logic so it can be tested with Jest/React Testing Library
- Use PascalCase for components, camelCase for functions/variables
- Add comments for non-obvious logic, but keep code self-explanatory

### General Copilot Usage
- **Never:**
  - Mix business logic and UI
  - Hardcode API URLs (use config/constants)
  - Duplicate code (extract helpers/components)
- **Always:**
  - Follow project folder structure
  - Use existing utilities/services when possible
  - Keep code readable and maintainable

---
For more details, see this file and project docs.
