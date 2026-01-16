"""World generator using prompts and algorithms."""

import random
from typing import Dict, Any, Optional, List
from models.world import World
from models.location import Location
from models.entity import Entity


class WorldGenerator:
    """Generates fictional worlds based on prompts."""
    
    # World type templates
    WORLD_TYPES = {
        "fantasy": {
            "themes": ["magic", "dragons", "kingdoms", "quests"],
            "location_types": ["castle", "forest", "mountain", "village", "dungeon"],
            "entity_types": ["wizard", "warrior", "dragon", "elf", "dwarf"]
        },
        "sci-fi": {
            "themes": ["space", "technology", "aliens", "future"],
            "location_types": ["space station", "planet", "spaceship", "colony", "laboratory"],
            "entity_types": ["android", "alien", "scientist", "pilot", "AI"]
        },
        "modern": {
            "themes": ["city", "technology", "society", "relationships"],
            "location_types": ["city", "office", "home", "park", "cafe"],
            "entity_types": ["professional", "student", "artist", "entrepreneur"]
        },
        "historical": {
            "themes": ["war", "politics", "culture", "exploration"],
            "location_types": ["palace", "battlefield", "temple", "marketplace", "port"],
            "entity_types": ["noble", "soldier", "merchant", "priest", "explorer"]
        }
    }
    
    def __init__(self):
        """Initialize the WorldGenerator."""
        pass
    
    def generate(
        self,
        prompt: str,
        world_type: str = "fantasy",
        metadata: Optional[Dict[str, Any]] = None
    ) -> World:
        """
        Generate a world based on a prompt.
        
        Args:
            prompt: User prompt describing the desired world
            world_type: Type of world (fantasy, sci-fi, modern, historical)
            metadata: Additional metadata
            
        Returns:
            Generated World object
        """
        # Extract world name from prompt or generate one
        name = self._extract_name(prompt) or self._generate_name(world_type)
        
        # Create world with enhanced description
        description = self._enhance_description(prompt, world_type)
        
        # Add world type to metadata
        world_metadata = metadata or {}
        world_metadata["world_type"] = world_type
        world_metadata["prompt"] = prompt
        
        if world_type in self.WORLD_TYPES:
            world_metadata["themes"] = self.WORLD_TYPES[world_type]["themes"]
        
        world = World(
            name=name,
            description=description,
            metadata=world_metadata
        )
        
        return world
    
    def generate_locations(
        self,
        world: World,
        count: int = 3
    ) -> List[Location]:
        """
        Generate locations for a world.
        
        Args:
            world: World to generate locations for
            count: Number of locations to generate
            
        Returns:
            List of generated Location objects
        """
        locations = []
        world_type = world.metadata.get("world_type", "fantasy")
        
        if world_type in self.WORLD_TYPES:
            location_types = self.WORLD_TYPES[world_type]["location_types"]
        else:
            location_types = ["location"]
        
        for i in range(count):
            location_type = random.choice(location_types)
            name = f"{location_type.title()} {i + 1}"
            description = f"A {location_type} in the world of {world.name}"
            
            # Generate random coordinates
            coordinates = {
                "x": random.uniform(-1000, 1000),
                "y": random.uniform(-1000, 1000),
                "z": random.uniform(0, 100)
            }
            
            location = Location(
                name=name,
                description=description,
                world_id=world.world_id,
                coordinates=coordinates,
                metadata={"location_type": location_type}
            )
            
            locations.append(location)
            world.add_location(location.location_id)
        
        return locations
    
    def generate_entities(
        self,
        world: World,
        count: int = 3
    ) -> List[Entity]:
        """
        Generate entities for a world.
        
        Args:
            world: World to generate entities for
            count: Number of entities to generate
            
        Returns:
            List of generated Entity objects
        """
        entities = []
        world_type = world.metadata.get("world_type", "fantasy")
        
        if world_type in self.WORLD_TYPES:
            entity_types = self.WORLD_TYPES[world_type]["entity_types"]
        else:
            entity_types = ["character"]
        
        for i in range(count):
            entity_type = random.choice(entity_types)
            name = f"{entity_type.title()} {i + 1}"
            description = f"A {entity_type} character in {world.name}"
            
            # Generate random attributes
            attributes = {
                "strength": random.randint(1, 10),
                "intelligence": random.randint(1, 10),
                "charisma": random.randint(1, 10)
            }
            
            entity = Entity(
                name=name,
                entity_type=entity_type,
                description=description,
                world_id=world.world_id,
                attributes=attributes
            )
            
            entities.append(entity)
            world.add_entity(entity.entity_id)
        
        return entities
    
    def _extract_name(self, prompt: str) -> Optional[str]:
        """Extract world name from prompt."""
        # Simple extraction - look for "world of" or "called"
        keywords = ["world of ", "called ", "named "]
        prompt_lower = prompt.lower()
        
        for keyword in keywords:
            if keyword in prompt_lower:
                idx = prompt_lower.index(keyword) + len(keyword)
                # Get the next few words
                remaining = prompt[idx:].split()
                if remaining:
                    return " ".join(remaining[:3]).strip('.,!?')
        
        return None
    
    def _generate_name(self, world_type: str) -> str:
        """Generate a world name based on type."""
        prefixes = {
            "fantasy": ["Mystic", "Ancient", "Eternal", "Lost", "Hidden"],
            "sci-fi": ["Nova", "Quantum", "Stellar", "Cyber", "Neo"],
            "modern": ["New", "Metro", "Urban", "Central", "Modern"],
            "historical": ["Ancient", "Imperial", "Royal", "Classical", "Old"]
        }
        
        suffixes = {
            "fantasy": ["Realm", "Kingdom", "Empire", "Land", "World"],
            "sci-fi": ["System", "Sector", "Galaxy", "Expanse", "Cluster"],
            "modern": ["City", "State", "Nation", "District", "Zone"],
            "historical": ["Empire", "Kingdom", "Dynasty", "Republic", "Realm"]
        }
        
        prefix_list = prefixes.get(world_type, ["New"])
        suffix_list = suffixes.get(world_type, ["World"])
        
        prefix = random.choice(prefix_list)
        suffix = random.choice(suffix_list)
        
        return f"{prefix} {suffix}"
    
    def _enhance_description(self, prompt: str, world_type: str) -> str:
        """Enhance the description based on prompt and world type."""
        base_description = prompt
        
        if world_type in self.WORLD_TYPES:
            themes = self.WORLD_TYPES[world_type]["themes"]
            theme_text = ", ".join(themes[:3])
            base_description += f" This {world_type} world features elements of {theme_text}."
        
        return base_description
