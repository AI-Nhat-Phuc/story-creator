# Models & Data Structures Guide - Story Creator

## Tổng Quan

Story Creator sử dụng 5 core models để represent data:
1. **World** - Thế giới chứa stories, entities, locations
2. **Story** - Câu chuyện trong thế giới
3. **Entity** - Nhân vật/Sinh vật
4. **Location** - Địa điểm
5. **TimeCone** - Temporal context cho stories

## Model Structure

### File Layout
```
core/
  └── models/
      ├── __init__.py
      ├── world.py          # World model
      ├── story.py          # Story model
      ├── entity.py         # Entity model
      ├── location.py       # Location model
      └── time_cone.py      # TimeCone model
```

## Model Pattern

Tất cả models follow cùng 1 pattern:

```python
class Model:
    def __init__(self, ...):
        """Initialize model với required và optional fields"""
        pass

    def to_dict(self) -> dict:
        """Convert model → Python dict"""
        pass

    def to_json(self) -> str:
        """Convert model → JSON string"""
        pass

    @classmethod
    def from_dict(cls, data: dict):
        """Create model từ dict"""
        pass

    @classmethod
    def from_json(cls, json_str: str):
        """Create model từ JSON string"""
        pass
```

## World Model

### Fields

```python
class World:
    world_id: str              # UUID, auto-generated
    name: str                  # Tên thế giới
    world_type: str            # fantasy/sci-fi/modern/historical
    description: str           # Mô tả thế giới
    entities: List[str]        # List of entity IDs
    locations: List[str]       # List of location IDs
    stories: List[str]         # List of story IDs
    metadata: dict             # Additional data
    created_at: str            # ISO timestamp
```

### Usage

```python
from core.models import World

# Create new world
world = World(
    name="Middle Earth",
    world_type="fantasy",
    description="A world of magic and adventure"
)

# Access fields
print(world.world_id)      # Auto-generated UUID
print(world.created_at)    # ISO timestamp

# Add entities/locations/stories
world.add_entity(entity_id)
world.add_location(location_id)
world.add_story(story_id)

# Serialize
world_dict = world.to_dict()
world_json = world.to_json()

# Deserialize
world = World.from_dict(world_dict)
world = World.from_json(world_json)
```

### World Types

| Type | Description | Themes |
|------|-------------|--------|
| `fantasy` | Magic, medieval | Dragons, castles, wizards |
| `sci-fi` | Future, space | Spaceships, aliens, AI |
| `modern` | Contemporary | Cities, technology |
| `historical` | Past events | Real historical periods |

### Methods

```python
# Add relationships
world.add_entity(entity_id: str)      # Add entity to world
world.add_location(location_id: str)  # Add location to world
world.add_story(story_id: str)        # Add story to world

# Remove relationships
world.remove_entity(entity_id: str)
world.remove_location(location_id: str)
world.remove_story(story_id: str)

# Check existence
has_entity = entity_id in world.entities
has_location = location_id in world.locations
has_story = story_id in world.stories
```

## Story Model

### Fields

```python
class Story:
    story_id: str              # UUID, auto-generated
    world_id: str              # Parent world ID
    title: str                 # Story title
    genre: str                 # adventure/mystery/conflict/discovery
    description: str           # Story content
    entities: List[str]        # Characters in story
    locations: List[str]       # Places in story
    metadata: dict             # Additional data
    created_at: str            # ISO timestamp
```

### Usage

```python
from core.models import Story

# Create story
story = Story(
    title="The Quest",
    world_id=world.world_id,
    genre="adventure",
    description="A hero embarks on a dangerous journey...",
    entities=[hero_id, wizard_id],
    locations=[castle_id, forest_id]
)

# Serialize/Deserialize
story_dict = story.to_dict()
story = Story.from_dict(story_dict)
```

### Story Genres

| Genre | Description | Template Elements |
|-------|-------------|-------------------|
| `adventure` | Journey, quest | Hero, obstacle, treasure |
| `mystery` | Investigation | Detective, clues, villain |
| `conflict` | Battle, war | Enemies, battle, resolution |
| `discovery` | Exploration | Explorer, new world, finding |

### Story Linking

Stories are automatically linked by:
1. **Shared Entities** - Same characters
2. **Shared Locations** - Same places
3. **Time Proximity** - Similar time_index

```python
from generators import StoryLinker

linker = StoryLinker()
links = linker.find_story_links([story1, story2, story3])

# Returns:
# [
#   {
#     'story1_id': 'uuid1',
#     'story2_id': 'uuid2',
#     'shared_entities': ['entity1', 'entity2'],
#     'shared_locations': ['location1'],
#     'link_strength': 0.85
#   }
# ]
```

## Entity Model

### Fields

```python
class Entity:
    entity_id: str                    # UUID, auto-generated
    world_id: str                     # Parent world ID
    name: str                         # Entity name
    entity_type: str                  # warrior/mage/ruler/merchant/creature
    description: str                  # Description
    attributes: Dict[str, int]        # Strength/Intelligence/Charisma (0-10)
    metadata: dict                    # Additional data
    created_at: str                   # ISO timestamp
```

### Usage

```python
from core.models import Entity

# Create entity
entity = Entity(
    name="Arthur",
    world_id=world.world_id,
    entity_type="warrior",
    description="A brave knight",
    attributes={
        "Strength": 8,
        "Intelligence": 6,
        "Charisma": 7
    }
)

# Access attributes
strength = entity.attributes.get("Strength", 5)

# Serialize/Deserialize
entity_dict = entity.to_dict()
entity = Entity.from_dict(entity_dict)
```

### Entity Types

| Type | Description | Typical Attributes |
|------|-------------|-------------------|
| `warrior` | Fighter, knight | High Strength |
| `mage` | Wizard, sorcerer | High Intelligence |
| `ruler` | King, leader | High Charisma |
| `merchant` | Trader | Medium all |
| `commoner` | Civilian | Low all |
| `creature` | Beast, monster | Varies |
| `dangerous_creature` | Boss monster | Very high |

### Attributes

All entities have 3 core attributes:
- **Strength** (0-10): Physical power, combat ability
- **Intelligence** (0-10): Mental capacity, magic ability
- **Charisma** (0-10): Social skills, leadership

```python
# Create balanced character
entity = Entity(
    name="Balanced Hero",
    entity_type="warrior",
    attributes={
        "Strength": 7,
        "Intelligence": 6,
        "Charisma": 7
    }
)

# Create specialized character
mage = Entity(
    name="Archmage",
    entity_type="mage",
    attributes={
        "Strength": 3,
        "Intelligence": 10,
        "Charisma": 6
    }
)
```

## Location Model

### Fields

```python
class Location:
    location_id: str              # UUID, auto-generated
    world_id: str                 # Parent world ID
    name: str                     # Location name
    description: str              # Description
    coordinates: Dict[str, float] # x, y coordinates
    metadata: dict                # Additional data
    created_at: str               # ISO timestamp
```

### Usage

```python
from core.models import Location

# Create location
location = Location(
    name="Dragon's Peak",
    world_id=world.world_id,
    description="A dangerous mountain peak",
    coordinates={"x": 100.5, "y": 250.3}
)

# Access coordinates
x = location.coordinates["x"]
y = location.coordinates["y"]

# Serialize/Deserialize
location_dict = location.to_dict()
location = Location.from_dict(location_dict)
```

### Coordinate System

- **Origin**: (0, 0) = Center of world
- **Range**: Typically -1000 to +1000 for both x and y
- **Units**: Abstract units (not meters/km)

```python
# Calculate distance between locations
import math

def distance(loc1, loc2):
    dx = loc1.coordinates["x"] - loc2.coordinates["x"]
    dy = loc1.coordinates["y"] - loc2.coordinates["y"]
    return math.sqrt(dx**2 + dy**2)

dist = distance(castle, forest)
print(f"Distance: {dist:.2f}")
```

## TimeCone Model

### Fields

```python
class TimeCone:
    time_cone_id: str             # UUID, auto-generated
    world_id: str                 # Parent world ID
    story_id: str                 # Associated story ID
    time_index: int               # 0-100, temporal position
    description: str              # Event description
    metadata: dict                # Additional data
    created_at: str               # ISO timestamp
```

### Usage

```python
from core.models import TimeCone

# Create time cone
time_cone = TimeCone(
    world_id=world.world_id,
    story_id=story.story_id,
    time_index=25,
    description="The hero's journey begins"
)

# Serialize/Deserialize
tc_dict = time_cone.to_dict()
time_cone = TimeCone.from_dict(tc_dict)
```

### Time Index System

- **Range**: 0-100
- **0**: Beginning of world timeline
- **100**: End/Current time
- **Purpose**: Order stories chronologically

```python
# Sort stories by time
stories_with_time = []
for story in stories:
    time_cone = storage.load_time_cone_by_story(story.story_id)
    if time_cone:
        stories_with_time.append((story, time_cone.time_index))

# Sort by time_index
stories_with_time.sort(key=lambda x: x[1])

# Read in chronological order
for story, time_idx in stories_with_time:
    print(f"[T={time_idx}] {story.title}")
```

## Serialization Examples

### to_dict() / from_dict()

```python
# World example
world = World(name="Test", world_type="fantasy")

# Convert to dict
world_dict = world.to_dict()
# {
#   'world_id': 'uuid-here',
#   'name': 'Test',
#   'world_type': 'fantasy',
#   'description': '',
#   'entities': [],
#   'locations': [],
#   'stories': [],
#   'metadata': {},
#   'created_at': '2026-01-18T14:30:00'
# }

# Convert back to object
world2 = World.from_dict(world_dict)
assert world.world_id == world2.world_id
```

### to_json() / from_json()

```python
# Entity example
entity = Entity(name="Hero", entity_type="warrior", world_id="world-123")

# Convert to JSON string
json_str = entity.to_json()
# '{"entity_id": "...", "name": "Hero", ...}'

# Convert back to object
entity2 = Entity.from_json(json_str)
assert entity.entity_id == entity2.entity_id
```

## Relationships

### World → Stories/Entities/Locations

```python
# One-to-Many relationship
world = World(name="Test World")
world.add_story(story1.story_id)
world.add_story(story2.story_id)
world.add_entity(entity1.entity_id)
world.add_location(location1.location_id)

# Access relationships
for story_id in world.stories:
    story = storage.load_story(story_id)
    print(story.title)
```

### Story → Entities/Locations

```python
# Many-to-Many relationship
story = Story(
    title="Adventure",
    world_id=world.world_id,
    entities=[hero_id, villain_id],
    locations=[castle_id, forest_id]
)

# Same entity can appear in multiple stories
story1.entities = [hero_id]
story2.entities = [hero_id]  # Same hero
```

### Story ↔ TimeCone

```python
# One-to-One relationship
story = Story(...)
time_cone = TimeCone(
    world_id=story.world_id,
    story_id=story.story_id,
    time_index=50
)

# Retrieve time cone for story
time_cone = storage.load_time_cone_by_story(story.story_id)
```

## Validation

### Required Fields

```python
# These will raise error if missing
world = World(
    name="Test",           # Required
    world_type="fantasy"   # Required
)

entity = Entity(
    name="Hero",           # Required
    world_id="uuid",       # Required
    entity_type="warrior"  # Required
)
```

### Field Constraints

```python
# World type validation
valid_types = ['fantasy', 'sci-fi', 'modern', 'historical']
assert world.world_type in valid_types

# Attribute range validation
for attr, value in entity.attributes.items():
    assert 0 <= value <= 10

# Time index validation
assert 0 <= time_cone.time_index <= 100
```

## Helper Functions

### Character Service

```python
from services import CharacterService

# Detect mentioned characters
description = "Arthur and Merlin went to the castle"
entity_data_list = [hero_data, mage_data]

names, ids = CharacterService.detect_mentioned_characters(
    description, entity_data_list
)
# names = ["Arthur", "Merlin"]
# ids = [hero_id, mage_id]

# Format display
display = CharacterService.format_character_display(hero_data)
# "👤 Arthur (warrior)"

# Get character names (exclude dangerous)
names = CharacterService.get_character_names(entity_data_list)
# ["Arthur", "Merlin"]  (excludes "Dangerous Dragon")
```

## Best Practices

### 1. Use Models, Not Raw Dicts

```python
# ✅ Good
world = World.from_dict(storage.load_world(world_id))
world.add_story(story_id)
storage.save_world(world.to_dict())

# ❌ Bad
world_data = storage.load_world(world_id)
world_data['stories'].append(story_id)
storage.save_world(world_data)
```

### 2. Check None Before Conversion

```python
# ✅ Good
world_data = storage.load_world(world_id)
if world_data:
    world = World.from_dict(world_data)
else:
    print("World not found")

# ❌ Bad (may crash)
world = World.from_dict(storage.load_world(world_id))
```

### 3. Use Type Hints

```python
from typing import List, Dict, Optional

def get_world_stories(world: World) -> List[Story]:
    """Get all stories in a world"""
    stories = []
    for story_id in world.stories:
        story_data = storage.load_story(story_id)
        if story_data:
            stories.append(Story.from_dict(story_data))
    return stories
```

### 4. Validate Before Save

```python
def create_entity(name: str, world_id: str, entity_type: str, attributes: dict):
    # Validate attributes
    for attr in ['Strength', 'Intelligence', 'Charisma']:
        if attr not in attributes:
            attributes[attr] = 5  # Default

        # Clamp to range
        attributes[attr] = max(0, min(10, attributes[attr]))

    entity = Entity(
        name=name,
        world_id=world_id,
        entity_type=entity_type,
        attributes=attributes
    )

    return entity
```

## Advanced Usage

### Custom Metadata

```python
# Add custom fields without modifying model
entity = Entity(name="Hero", entity_type="warrior", world_id="w1")
entity.metadata = {
    "level": 10,
    "experience": 5000,
    "inventory": ["sword", "shield"],
    "quests_completed": 15
}

storage.save_entity(entity.to_dict())

# Retrieve custom data
entity = Entity.from_dict(storage.load_entity(entity_id))
level = entity.metadata.get("level", 1)
```

### Extending Models

```python
# Create subclass for game-specific logic
class GameEntity(Entity):
    def level_up(self):
        """Increase attributes on level up"""
        self.metadata["level"] = self.metadata.get("level", 1) + 1

        # Increase random attribute
        import random
        attr = random.choice(["Strength", "Intelligence", "Charisma"])
        self.attributes[attr] = min(10, self.attributes[attr] + 1)

    def add_item(self, item_name: str):
        """Add item to inventory"""
        inventory = self.metadata.get("inventory", [])
        inventory.append(item_name)
        self.metadata["inventory"] = inventory
```

## Next Steps

1. 📖 Đọc [STORAGE_GUIDE.md](STORAGE_GUIDE.md) để hiểu cách lưu models
2. 🔧 Đọc [GENERATORS_GUIDE.md](GENERATORS_GUIDE.md) để tạo models tự động
3. 🧪 Test với `test.py` để xem models hoạt động
