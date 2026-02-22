# api/

All Python backend code for Story Creator.

## Structure

- `app.py` — Vercel serverless entrypoint (exposes `app` for WSGI)
- `main.py` — Local dev entrypoint (argument parsing, interface routing)
- `requirements.txt` — Python dependencies
- `ai/` — GPT-4o-mini integration (client, prompts, simulation)
- `core/models/` — Domain models (World, Story, Entity, Location, TimeCone)
- `generators/` — Content generators + story linker
- `interfaces/` — Flask API + blueprint routes
- `services/` — Business logic (GPTService, CharacterService)
- `storage/` — NoSQL (TinyDB) + JSON storage backends
- `visualization/` — Relationship diagram generation

## Import Convention

All imports inside `api/` use **bare module names** (no `api.*` prefix):

```python
from core.models import World, Entity
from storage import NoSQLStorage
from services import GPTService
from ai.gpt_client import GPTIntegration
```

This works because both `app.py` and `main.py` add `api/` to `sys.path`.

## Running

```bash
# Local dev
.venv\Scripts\python.exe api/main.py -i api

# On Vercel — api/app.py is auto-detected as serverless function
```
