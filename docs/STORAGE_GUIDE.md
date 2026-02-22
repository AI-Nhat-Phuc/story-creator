# Storage Layer Guide - Story Creator

## Tổng Quan

Story Creator hỗ trợ 2 storage backends:
1. **NoSQL Database** (TinyDB) - **RECOMMENDED** - Mặc định
2. **JSON Files** - Legacy, cho debugging

## Storage Backends Comparison

| Feature | NoSQL (TinyDB) | JSON Files |
|---------|---------------|------------|
| **Speed** | ⚡ Fast (10-100x) | 🐌 Slow |
| **Query** | ✅ Indexed queries | ❌ Full scan |
| **File Count** | 1 file (.db) | Many files |
| **Recommended For** | Production, >50 items | Small datasets, debugging |
| **Memory Usage** | Low | Medium |
| **Thread Safety** | ✅ Yes | ⚠️ Limited |

## NoSQL Storage (TinyDB)

### File Structure
```
storage/
  ├── __init__.py
  ├── base_storage.py          # Abstract base class
  ├── nosql_storage.py         # TinyDB implementation ⭐
  └── json_storage.py          # JSON implementation
```

### Initialization

```python
from storage import NoSQLStorage

# Create storage instance
storage = NoSQLStorage(db_path="story_creator.db")

# Auto-creates database file if not exists
# Creates tables: worlds, stories, entities, locations, time_cones
```

### Database Schema

**Tables**:
- `worlds` - World data
- `stories` - Story data
- `entities` - Character/creature data
- `locations` - Place data
- `time_cones` - Temporal context data

**Document Structure**: Each document = Python dict with all model fields

### CRUD Operations

#### Create (Save)

```python
from core.models import World, Entity

# Create model
world = World(
    name="Fantasy Realm",
    description="A magical world",
    world_type="fantasy"
)

# Save to database
storage.save_world(world.to_dict())

# Entity example
entity = Entity(
    name="Hero",
    entity_type="warrior",
    world_id=world.world_id,
    description="Brave knight",
    attributes={"Strength": 8, "Intelligence": 6, "Charisma": 7}
)

storage.save_entity(entity.to_dict())
```

**How It Works**:
1. Check if document với matching ID đã tồn tại
2. Nếu có: **Update** existing document
3. Nếu không: **Insert** new document
4. Auto-commit (TinyDB default behavior)

#### Read (Load)

```python
# Load by ID
world_data = storage.load_world(world_id)
# Returns: dict hoặc None nếu không tìm thấy

entity_data = storage.load_entity(entity_id)
story_data = storage.load_story(story_id)
location_data = storage.load_location(location_id)
time_cone_data = storage.load_time_cone(time_cone_id)
```

**Convert to Model**:
```python
from core.models import World

world_data = storage.load_world(world_id)
if world_data:
    world = World.from_dict(world_data)
```

#### List (Query)

```python
# List all worlds
worlds = storage.list_worlds()
# Returns: list of dicts

# List stories in a world
stories = storage.list_stories(world_id)

# List entities in a world
entities = storage.list_entities(world_id)

# List locations in a world
locations = storage.list_locations(world_id)

# List time cones in a world
time_cones = storage.list_time_cones(world_id)
```

**Filter by World**:
```python
# Internally uses TinyDB Query
from tinydb import Query

StoryQuery = Query()
stories = self.stories.search(StoryQuery.world_id == world_id)
```

#### Update

```python
# Load existing
world_data = storage.load_world(world_id)
world = World.from_dict(world_data)

# Modify
world.name = "Updated Name"
world.add_story(new_story_id)

# Save (upsert behavior)
storage.save_world(world.to_dict())
```

#### Delete

```python
# Delete world
storage.delete_world(world_id)

# Delete all related data (manual cleanup)
stories = storage.list_stories(world_id)
for story in stories:
    storage.delete_story(story['story_id'])

entities = storage.list_entities(world_id)
for entity in entities:
    storage.delete_entity(entity['entity_id'])
```

### Advanced Queries

#### Custom TinyDB Queries

```python
from tinydb import Query

# Access tables directly
worlds_table = storage.worlds

# Query by multiple conditions
WorldQuery = Query()
fantasy_worlds = worlds_table.search(
    WorldQuery.world_type == 'fantasy'
)

# Query with operators
strong_entities = storage.entities.search(
    (Query().attributes.Strength > 7) &
    (Query().entity_type == 'warrior')
)

# Count documents
total_worlds = len(storage.worlds)
```

#### Statistics

```python
stats = storage.get_stats()
# Returns:
# {
#     'total_worlds': 10,
#     'total_stories': 45,
#     'total_entities': 120,
#     'total_locations': 35,
#     'total_time_cones': 45
# }
```

### Database Maintenance

#### Flush Data

```python
# Force write to disk (usually auto)
storage.flush()
```

#### Clear All Data

```python
# Clear specific table
storage.worlds.purge()

# Or delete database file
import os
os.remove("story_creator.db")
```

#### Backup

```python
import shutil
from datetime import datetime

# Create backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy("story_creator.db", f"backup_{timestamp}.db")
```

### Performance Optimization

#### Indexing
TinyDB doesn't support traditional indexes, but uses:
- **Document ID lookup**: O(1)
- **Query with ID**: O(1)
- **Full table scan**: O(n)

**Best Practices**:
- ✅ Load by ID khi có thể
- ✅ Filter in Python sau khi load nếu dataset nhỏ
- ❌ Avoid nested queries trong large datasets

#### Caching Pattern

```python
class CachedStorage:
    def __init__(self, storage):
        self.storage = storage
        self.world_cache = {}

    def load_world(self, world_id):
        if world_id not in self.world_cache:
            self.world_cache[world_id] = self.storage.load_world(world_id)
        return self.world_cache[world_id]
```

## JSON Storage (Legacy)

### File Structure

```
data/
  ├── worlds/
  │   ├── world_uuid1.json
  │   └── world_uuid2.json
  ├── stories/
  │   ├── story_uuid1.json
  │   └── story_uuid2.json
  ├── entities/
  ├── locations/
  └── time_cones/
```

### Usage

```python
from storage import JSONStorage

# Initialize (creates directories)
storage = JSONStorage(data_dir="data")

# Same API as NoSQL
storage.save_world(world.to_dict())
world_data = storage.load_world(world_id)
```

### When to Use JSON

✅ **Good for**:
- Debugging (easy to inspect files)
- Version control (git diff readable)
- Small datasets (<50 items per type)
- Quick prototyping

❌ **Avoid for**:
- Production use
- Large datasets (>100 items)
- Concurrent access
- Performance-critical apps

## Choosing Storage Type

### Command Line

```bash
# NoSQL (default)
.venv\Scripts\python.exe api/main.py -i api -s nosql

# JSON
.venv\Scripts\python.exe api/main.py -i api -s json

# Simulation with NoSQL
.venv\Scripts\python.exe api/main.py -i simulation -s nosql
```

### Programmatic

```python
# main.py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--storage', choices=['nosql', 'json'], default='nosql')

args = parser.parse_args()

if args.storage == 'nosql':
    storage = NoSQLStorage("story_creator.db")
else:
    storage = JSONStorage("data")
```

## Data Migration

### JSON → NoSQL

```python
from storage import JSONStorage, NoSQLStorage

# Load from JSON
json_storage = JSONStorage("data")
nosql_storage = NoSQLStorage("story_creator.db")

# Migrate worlds
for world_file in os.listdir("data/worlds"):
    world_id = world_file.replace(".json", "")
    world_data = json_storage.load_world(world_id)
    if world_data:
        nosql_storage.save_world(world_data)

# Repeat for stories, entities, locations, time_cones
print("✅ Migration complete")
```

### NoSQL → JSON (Backup)

```python
nosql_storage = NoSQLStorage("story_creator.db")
json_storage = JSONStorage("backup_data")

# Export all worlds
for world_data in nosql_storage.list_worlds():
    json_storage.save_world(world_data)

# Repeat for other types
```

## Data Validation

### Schema Validation (Optional)

```python
def validate_world_data(world_data):
    """Validate world data before saving"""
    required_fields = ['world_id', 'name', 'world_type', 'description']

    for field in required_fields:
        if field not in world_data:
            raise ValueError(f"Missing required field: {field}")

    if world_data['world_type'] not in ['fantasy', 'sci-fi', 'modern', 'historical']:
        raise ValueError("Invalid world_type")

    return True

# Use before saving
if validate_world_data(world.to_dict()):
    storage.save_world(world.to_dict())
```

### Data Integrity

```python
def check_orphan_stories(storage):
    """Find stories without valid world_id"""
    all_stories = storage.list_stories()
    orphans = []

    for story_data in all_stories:
        world_id = story_data.get('world_id')
        world_data = storage.load_world(world_id)

        if not world_data:
            orphans.append(story_data['story_id'])

    return orphans

# Run check
orphans = check_orphan_stories(storage)
if orphans:
    print(f"⚠️ Found {len(orphans)} orphan stories")
```

## Error Handling

### File Access Errors

```python
try:
    storage = NoSQLStorage("readonly/story_creator.db")
except PermissionError:
    print("❌ No permission to access database")
except Exception as e:
    print(f"❌ Database error: {e}")
```

### Data Not Found

```python
world_data = storage.load_world(world_id)
if not world_data:
    print(f"⚠️ World {world_id} not found")
    # Handle gracefully
else:
    world = World.from_dict(world_data)
```

### Corrupted Data

```python
try:
    world_data = storage.load_world(world_id)
    world = World.from_dict(world_data)
except (KeyError, ValueError) as e:
    print(f"❌ Corrupted data: {e}")
    # Delete or repair
    storage.delete_world(world_id)
```

## Testing Storage

### Unit Tests

```python
# test_storage.py
import unittest
from storage import NoSQLStorage
from core.models import World

class TestNoSQLStorage(unittest.TestCase):
    def setUp(self):
        self.storage = NoSQLStorage("test.db")

    def tearDown(self):
        import os
        os.remove("test.db")

    def test_save_and_load_world(self):
        world = World(name="Test World", world_type="fantasy")
        self.storage.save_world(world.to_dict())

        loaded = self.storage.load_world(world.world_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded['name'], "Test World")

    def test_list_worlds(self):
        world1 = World(name="World 1", world_type="fantasy")
        world2 = World(name="World 2", world_type="sci-fi")

        self.storage.save_world(world1.to_dict())
        self.storage.save_world(world2.to_dict())

        worlds = self.storage.list_worlds()
        self.assertEqual(len(worlds), 2)
```

### Performance Tests

```bash
# test_nosql.py - Benchmark NoSQL vs JSON
.venv\Scripts\python.exe api/test_nosql.py

# Expected output:
# ⚡ NoSQL: 100 saves in 0.25s
# 🐌 JSON: 100 saves in 2.34s
# 📊 NoSQL is 9.4x faster
```

## Best Practices

### 1. Always Use NoSQL for Production
```python
# ✅ Good
storage = NoSQLStorage("story_creator.db")

# ❌ Avoid for production
storage = JSONStorage("data")
```

### 2. Check Existence Before Operations
```python
# ✅ Good
world_data = storage.load_world(world_id)
if world_data:
    world = World.from_dict(world_data)
    # Process...

# ❌ Bad (may crash)
world = World.from_dict(storage.load_world(world_id))
```

### 3. Use Models for Type Safety
```python
# ✅ Good
world = World.from_dict(world_data)
world.add_story(story_id)
storage.save_world(world.to_dict())

# ❌ Bad (error-prone)
world_data['stories'].append(story_id)
storage.save_world(world_data)
```

### 4. Flush After Critical Operations
```python
# ✅ Good for critical saves
storage.save_world(world.to_dict())
storage.flush()

# ⚠️ Normal saves auto-flush
```

### 5. Clean Up Related Data
```python
# ✅ Good - delete all related entities
def delete_world_cascade(storage, world_id):
    # Delete stories
    for story in storage.list_stories(world_id):
        storage.delete_story(story['story_id'])

    # Delete entities
    for entity in storage.list_entities(world_id):
        storage.delete_entity(entity['entity_id'])

    # Delete locations
    for location in storage.list_locations(world_id):
        storage.delete_location(location['location_id'])

    # Delete world
    storage.delete_world(world_id)
```

## Troubleshooting

### Database Locked

**Symptom**: `DatabaseError: database is locked`

**Solution**:
```python
# Close all connections
storage.close()

# Or delete .db file và restart
```

### Slow Queries

**Symptom**: `list_stories()` takes >1 second

**Solution**:
1. Check dataset size
2. Use filtering after load
3. Consider pagination
4. Cache frequently accessed data

### Corrupted Database

**Symptom**: Can't open .db file

**Solution**:
```bash
# Restore from backup
copy backup_20260118_143000.db story_creator.db

# Or start fresh
del story_creator.db
.venv\Scripts\python.exe api/main.py -i api
```

## Advanced Topics

### Custom Storage Backend

```python
from storage.base_storage import BaseStorage

class MongoDBStorage(BaseStorage):
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)
        self.db = self.client['story_creator']

    def save_world(self, world_data):
        self.db.worlds.update_one(
            {'world_id': world_data['world_id']},
            {'$set': world_data},
            upsert=True
        )

    # Implement all abstract methods...
```

### Multi-Database Setup

```python
# Use different databases per world
class MultiDBStorage:
    def __init__(self, base_path):
        self.base_path = base_path
        self.storages = {}

    def get_storage(self, world_id):
        if world_id not in self.storages:
            db_path = f"{self.base_path}/{world_id}.db"
            self.storages[world_id] = NoSQLStorage(db_path)
        return self.storages[world_id]
```

## Next Steps

1. 📖 Đọc [MODELS_GUIDE.md](MODELS_GUIDE.md) để hiểu data structures
2. 🧪 Chạy `test_nosql.py` để xem performance comparison
3. 🔧 Đọc [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) để customize storage
