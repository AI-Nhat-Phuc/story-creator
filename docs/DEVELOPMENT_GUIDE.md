# Development Guide - Story Creator

## Getting Started

### Prerequisites

- **Python**: 3.7+ (recommended: 3.11+)
- **Git**: For version control
- **VS Code**: Recommended IDE
- **Virtual Environment**: Isolated Python environment

### Initial Setup

```bash
# 1. Clone repository (nếu có)
git clone <repository-url>
cd story-creator

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file for GPT
# Copy .env.example nếu có, hoặc tạo mới:
echo OPENAI_API_KEY=your-key-here > .env

# 6. Test installation
python test.py
```

## Project Structure

```
story-creator/
├── .env                        # API keys (DO NOT COMMIT)
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── main.py                     # Entry point
├── README.md                   # Project overview
├── INSTALLATION.md             # Setup instructions
├── USAGE.md                    # Usage guide
│
├── .venv/                      # Virtual environment (DO NOT COMMIT)
│
├── ai/                         # GPT integration
│   ├── gpt_client.py          # OpenAI API wrapper
│   ├── prompts.py             # Prompt templates
│   └── simulation.py          # Simulation logic
│
├── core/                       # Core domain models
│   └── models/
│       ├── world.py
│       ├── story.py
│       ├── entity.py
│       ├── location.py
│       └── time_cone.py
│
├── generators/                 # Content generators
│   ├── world_generator.py     # World creation
│   ├── story_generator.py     # Story creation
│   └── story_linker.py        # Story linking logic
│
├── storage/                    # Data persistence
│   ├── base_storage.py        # Abstract base
│   ├── nosql_storage.py       # TinyDB backend
│   └── json_storage.py        # JSON backend
│
├── services/                   # Business logic layer
│   ├── gpt_service.py         # GPT async service
│   └── character_service.py   # Character utilities
│
├── interfaces/                 # User interfaces
│   ├── web_interface.py       # Flask web app
│   └── simulation_interface.py # Terminal simulation
│
├── templates/                  # HTML templates
│   └── index.html             # Main web UI
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── visualization/              # Visualization tools
│   └── relationship_diagram.py
│
├── docs/                       # Documentation
│   ├── WEB_INTERFACE_GUIDE.md
│   ├── GPT_INTEGRATION_GUIDE.md
│   ├── STORAGE_GUIDE.md
│   ├── MODELS_GUIDE.md
│   └── DEVELOPMENT_GUIDE.md    # This file
│
└── tests/                      # Test files
    ├── test.py
    ├── test_nosql.py
    └── test_api_key.py
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow coding standards (see below)

### 3. Test Changes

```bash
# Run all tests
python test.py
python test_nosql.py

# Test specific feature
python main.py -i web --debug
```

### 4. Commit & Push

```bash
git add .
git commit -m "Add: feature description"
git push origin feature/your-feature-name
```

## Coding Standards

### Python Style Guide (PEP 8)

```python
# ✅ Good: Snake case for variables/functions
def generate_world_description(world_type: str) -> str:
    world_data = {}
    return json.dumps(world_data)

# ✅ Good: Pascal case for classes
class WorldGenerator:
    def __init__(self):
        self.templates = {}

# ✅ Good: Type hints
def create_entity(name: str, entity_type: str) -> Entity:
    return Entity(name=name, entity_type=entity_type)

# ✅ Good: Docstrings
def save_world(world: World) -> bool:
    """
    Save world to database.

    Args:
        world: World object to save

    Returns:
        True if successful, False otherwise
    """
    pass
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Variables | snake_case | `world_id`, `entity_list` |
| Functions | snake_case | `generate_world()`, `save_entity()` |
| Classes | PascalCase | `WorldGenerator`, `NoSQLStorage` |
| Constants | UPPER_CASE | `MAX_ENTITIES`, `DEFAULT_WORLD_TYPE` |
| Private | _leading_underscore | `_internal_method()` |

### File Organization

```python
# 1. Imports (grouped)
# Standard library
import json
import uuid
from datetime import datetime

# Third-party
from flask import Flask, jsonify
from tinydb import TinyDB, Query

# Local
from core.models import World, Story
from storage import NoSQLStorage

# 2. Constants
DEFAULT_WORLD_TYPE = "fantasy"
MAX_ENTITIES = 100

# 3. Classes
class WorldGenerator:
    pass

# 4. Functions
def create_world(name: str) -> World:
    pass

# 5. Main execution
if __name__ == "__main__":
    pass
```

## Adding New Features

### Add New World Type

**Example**: Add "cyberpunk" world type

1. **Update world_generator.py**:
```python
WORLD_TYPES = {
    # ... existing types ...
    "cyberpunk": {
        "themes": ["technology", "corporations", "hackers"],
        "location_types": ["megacity", "server_farm", "nightclub"],
        "entity_types": ["hacker", "corporate", "android"]
    }
}
```

2. **Update templates/index.html**:
```html
<select id="worldType" class="select select-bordered">
    <option value="fantasy">Fantasy</option>
    <option value="sci-fi">Sci-Fi</option>
    <option value="modern">Modern</option>
    <option value="historical">Historical</option>
    <option value="cyberpunk">Cyberpunk</option> <!-- NEW -->
</select>
```

3. **Test**:
```python
world = world_generator.generate(
    "Neon city with hackers",
    world_type="cyberpunk"
)
```

### Add New API Endpoint

**Example**: Add endpoint to get random world

1. **Update web_interface.py** trong `_register_routes()`:
```python
@self.app.route('/api/worlds/random', methods=['GET'])
def get_random_world():
    """Get a random world"""
    import random

    worlds = self.storage.list_worlds()
    if not worlds:
        return jsonify({'error': 'No worlds found'}), 404

    random_world = random.choice(worlds)
    return jsonify(random_world)
```

2. **Add frontend function** trong `static/js/app.js`:
```javascript
async function loadRandomWorld() {
    const response = await fetch('/api/worlds/random');
    const world = await response.json();

    if (world.error) {
        showToast(world.error, 'error');
        return;
    }

    showWorldDetails(world.world_id);
}
```

3. **Add UI button** trong `templates/index.html`:
```html
<button class="btn btn-primary" onclick="loadRandomWorld()">
    🎲 Random World
</button>
```

### Add New Model Field

**Example**: Add "difficulty" field to Story

1. **Update core/models/story.py**:
```python
class Story:
    def __init__(
        self,
        title: str,
        world_id: str,
        genre: str = "adventure",
        description: str = "",
        entities: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        difficulty: int = 5,  # NEW: 1-10
        metadata: Optional[dict] = None
    ):
        # ... existing code ...
        self.difficulty = difficulty

    def to_dict(self) -> dict:
        return {
            # ... existing fields ...
            "difficulty": self.difficulty
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            # ... existing fields ...
            difficulty=data.get("difficulty", 5)
        )
```

2. **Update story_generator.py**:
```python
def generate(self, description, world_id, genre="adventure", difficulty=5, ...):
    story = Story(
        # ... existing fields ...
        difficulty=difficulty
    )
```

3. **Update web interface**:
```html
<!-- Add slider in story creation form -->
<div class="form-control">
    <label class="label">Difficulty: <span id="difficultyValue">5</span></label>
    <input type="range" id="difficulty" min="1" max="10" value="5"
           class="range range-primary"
           oninput="document.getElementById('difficultyValue').textContent = this.value">
</div>
```

```javascript
// Update createStoryForm()
const difficulty = parseInt(document.getElementById('difficulty').value);

const response = await fetch('/api/stories', {
    method: 'POST',
    body: JSON.stringify({
        // ... existing fields ...
        difficulty: difficulty
    })
});
```

### Add New GPT Prompt

**Example**: Add "generate location description" prompt

1. **Update ai/prompts.py**:
```python
LOCATION_DESCRIPTION_PROMPT = """
Generate a vivid description for this {world_type} location.

Location name: {name}
World context: {world_context}

Write 2-3 sentences describing the location's appearance, atmosphere, and significance.
"""
```

2. **Add method to gpt_client.py**:
```python
def generate_location_description(
    self,
    location_name: str,
    world_type: str,
    world_context: str
) -> str:
    """Generate description for a location"""
    from ai.prompts import LOCATION_DESCRIPTION_PROMPT

    prompt = LOCATION_DESCRIPTION_PROMPT.format(
        name=location_name,
        world_type=world_type,
        world_context=world_context
    )

    response = self.client.chat.completions.create(
        model=self.model,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=200
    )

    return response.choices[0].message.content.strip()
```

3. **Use in generator**:
```python
if self.gpt and self.gpt.is_available():
    description = self.gpt.generate_location_description(
        location_name=name,
        world_type=world_type,
        world_context=world.description
    )
else:
    description = f"A {name} in the world"
```

## Testing

### Unit Tests

```python
# test_world_generator.py
import unittest
from generators import WorldGenerator

class TestWorldGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = WorldGenerator()

    def test_generate_world(self):
        world = self.generator.generate(
            "Fantasy world",
            world_type="fantasy"
        )

        self.assertEqual(world.world_type, "fantasy")
        self.assertIsNotNone(world.world_id)
        self.assertTrue(len(world.world_id) > 0)

    def test_generate_entities(self):
        from core.models import World
        world = World(name="Test", world_type="fantasy")

        entities = self.generator.generate_entities(world, count=5)

        self.assertEqual(len(entities), 5)
        for entity in entities:
            self.assertEqual(entity.world_id, world.world_id)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```python
# test_integration.py
import unittest
from storage import NoSQLStorage
from generators import WorldGenerator, StoryGenerator
from core.models import World, Story

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.storage = NoSQLStorage("test_integration.db")
        self.world_gen = WorldGenerator()
        self.story_gen = StoryGenerator()

    def tearDown(self):
        import os
        os.remove("test_integration.db")

    def test_full_workflow(self):
        # Create world
        world = self.world_gen.generate("Fantasy", world_type="fantasy")
        self.storage.save_world(world.to_dict())

        # Create entities
        entities = self.world_gen.generate_entities(world, count=3)
        for entity in entities:
            self.storage.save_entity(entity.to_dict())
            world.add_entity(entity.entity_id)

        self.storage.save_world(world.to_dict())

        # Create story
        story = self.story_gen.generate(
            "Adventure story",
            world.world_id,
            entities=[entities[0].entity_id]
        )
        self.storage.save_story(story.to_dict())

        # Verify
        loaded_world = self.storage.load_world(world.world_id)
        self.assertIsNotNone(loaded_world)
        self.assertEqual(len(loaded_world['entities']), 3)
```

### Manual Testing Checklist

- [ ] Web interface loads without errors
- [ ] Can create world với/không GPT
- [ ] Can create story with auto character detection
- [ ] Can view world details (stories, characters, locations)
- [ ] GPT analysis works (if API key available)
- [ ] Statistics update correctly
- [ ] Toast notifications appear
- [ ] Forms validate input
- [ ] Responsive design works on mobile
- [ ] All tabs/sections functional

## Debugging

### VS Code Debug Configuration

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Web Interface",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "args": ["-i", "web", "--debug"],
            "console": "integratedTerminal",
            "python": "${workspaceFolder}/.venv/Scripts/python.exe"
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/test.py",
            "console": "integratedTerminal",
            "python": "${workspaceFolder}/.venv/Scripts/python.exe"
        }
    ]
}
```

### Logging

```python
# Add logging to debug issues
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use in code
logger.debug(f"Loading world: {world_id}")
logger.info("World created successfully")
logger.warning("GPT not available")
logger.error(f"Failed to save world: {error}")
```

### Common Issues

#### Import Errors
```bash
# Problem: ModuleNotFoundError
# Solution: Check virtual environment activated
.venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Port Already in Use
```bash
# Problem: Port 5000 already in use
# Solution: Kill process or use different port
python main.py -i web --port 8080
```

#### Database Locked
```bash
# Problem: Database is locked
# Solution: Close all connections and restart
# Or delete .db file
del story_creator.db
```

## Performance Optimization

### Database Queries

```python
# ❌ Bad: Load all then filter in Python
all_stories = storage.list_stories()
fantasy_stories = [s for s in all_stories if s.get('genre') == 'adventure']

# ✅ Good: Use TinyDB query
from tinydb import Query
StoryQuery = Query()
adventure_stories = storage.stories.search(StoryQuery.genre == 'adventure')
```

### Caching

```python
# Add simple cache for frequently accessed data
class CachedStorage:
    def __init__(self, storage):
        self.storage = storage
        self.cache = {}

    def load_world(self, world_id):
        if world_id not in self.cache:
            self.cache[world_id] = self.storage.load_world(world_id)
        return self.cache[world_id]

    def invalidate_cache(self, world_id):
        if world_id in self.cache:
            del self.cache[world_id]
```

### Frontend Optimization

```javascript
// Debounce character detection
let detectTimeout;
function onDescriptionChange() {
    clearTimeout(detectTimeout);
    detectTimeout = setTimeout(() => {
        detectCharactersInDescription();
    }, 500);  // Wait 500ms after user stops typing
}
```

## Deployment

### Local Production

```bash
# Use production-ready WSGI server
pip install gunicorn  # Linux/Mac
pip install waitress  # Windows

# Run with waitress
waitress-serve --host=127.0.0.1 --port=5000 --call 'interfaces.web_interface:create_app'
```

### Environment Variables

```bash
# .env for production
OPENAI_API_KEY=sk-proj-your-key
FLASK_ENV=production
SECRET_KEY=generate-strong-random-key
DATABASE_PATH=production.db
```

### Security Checklist

- [ ] Change Flask secret key
- [ ] Add authentication (if public)
- [ ] Use HTTPS
- [ ] Validate all user input
- [ ] Sanitize HTML output
- [ ] Rate limit API endpoints
- [ ] Keep dependencies updated
- [ ] Don't expose debug mode
- [ ] Secure .env file (never commit)

## Contributing

### Code Review Checklist

- [ ] Code follows PEP 8 style guide
- [ ] All functions have docstrings
- [ ] Type hints used where appropriate
- [ ] Tests added for new features
- [ ] No hardcoded credentials
- [ ] Error handling implemented
- [ ] Logging added for debugging
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if UI changes)
[Add screenshots]

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] Tests added/updated
```

## Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [TinyDB Documentation](https://tinydb.readthedocs.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [DaisyUI Components](https://daisyui.com/components/)

### Tools
- [VS Code](https://code.visualstudio.com/)
- [Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)

## Next Steps

1. 📖 Read all guides trong `docs/` folder
2. 🧪 Run all tests để verify setup
3. 🎮 Test web interface với sample data
4. 🔧 Make a small change và test workflow
5. 📝 Read existing code để understand patterns
