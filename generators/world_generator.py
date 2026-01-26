"""World generator using prompts and algorithms."""

import random
from typing import Dict, Any, Optional, List
from core.models import World, Location, Entity


class WorldGenerator:
    """Generates fictional worlds based on prompts."""

    # Vietnamese and English name pools
    PERSON_NAMES = {
        "male": ["Minh", "Tuấn", "Hùng", "Dũng", "Nam", "Khoa", "Phong", "Long", "Alex", "James", "David", "Michael", "John", "Robert"],
        "female": ["Hoa", "Linh", "Nga", "Mai", "Thu", "Lan", "Anh", "Trang", "Alice", "Emma", "Sarah", "Lisa", "Maria", "Anna"]
    }

    LOCATION_NAMES = {
        "forest": ["Rừng Xanh", "Rừng Sâu", "Rừng Mê", "Rừng Thiêng", "Greenwood", "Darkwood", "Silverleaf", "Ironbark"],
        "mountain": ["Núi Cao", "Núi Lửa", "Núi Tuyết", "Núi Thiêng", "Snowpeak", "Ironpeak", "Stormhaven", "Cloudrest"],
        "village": ["Làng Hoa", "Làng Sen", "Làng Tre", "Làng Cổ", "Greenhill", "Riverside", "Meadowbrook", "Stonehaven"],
        "city": ["Thành Hoa", "Thành Vàng", "Thành Phố Cổ", "Metropolis", "Capital City", "Harbor City", "Crystal City"],
        "castle": ["Lâu Đài Rồng", "Lâu Đài Đá", "Lâu Đài Bạc", "Dragon Keep", "Iron Fortress", "Silver Castle", "Storm Keep"],
        "river": ["Sông Xanh", "Sông Vàng", "Sông Đỏ", "Sông Thiêng", "Azure River", "Golden Stream", "Silver Flow", "Crystal Waters"],
        "lake": ["Hồ Xanh", "Hồ Ngọc", "Hồ Thiêng", "Sapphire Lake", "Crystal Lake", "Mirror Lake", "Moonlight Lake"],
        "dungeon": ["Hầm Sâu", "Hầm Tối", "Hầm Ma", "Dark Depths", "Shadow Pit", "Forgotten Crypt"],
        "space station": ["Trạm Không Gian Alpha", "Trạm Thiên Hà", "Starlight Station", "Orbital Prime", "Gateway Station"],
        "planet": ["Hành Tinh Xanh", "Hành Tinh Đỏ", "Nova Prime", "Terra Nova", "Crimson World"],
        "office": ["Văn Phòng Trung Tâm", "Tòa Nhà Kinh Doanh", "Central Office", "Business Tower"],
        "cafe": ["Quán Cà Phê Xanh", "Quán Hoa", "Green Cafe", "Rose Cafe", "Corner Coffee"],
        "palace": ["Cung Điện Vàng", "Cung Điện Hoàng Gia", "Royal Palace", "Imperial Hall"],
        "default": ["Địa Điểm Bí Ẩn", "Vùng Đất Xa", "Mysterious Place", "Unknown Territory"]
    }

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
        self.used_person_names = set()
        self.used_location_names = set()

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
            name = self._get_unique_location_name(location_type)
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

            # Determine gender for person names
            gender = "female" if "female" in entity_type.lower() else "male"
            name = self._get_unique_person_name(gender)

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

    def _get_unique_person_name(self, gender: str) -> str:
        """Get unique person name from pool."""
        gender = gender.lower()
        if gender not in self.PERSON_NAMES:
            gender = "male"  # Default

        available_names = [n for n in self.PERSON_NAMES[gender] if n not in self.used_person_names]

        if not available_names:
            # Pool exhausted, use numbered fallback
            return f"Person {len(self.used_person_names) + 1}"

        name = random.choice(available_names)
        self.used_person_names.add(name)
        return name

    def _get_unique_location_name(self, location_type: str) -> str:
        """Get unique location name from pool."""
        location_type = location_type.lower()
        if location_type not in self.LOCATION_NAMES:
            location_type = "village"  # Default

        available_names = [n for n in self.LOCATION_NAMES[location_type] if n not in self.used_location_names]

        if not available_names:
            # Pool exhausted, use numbered fallback
            return f"{location_type.title()} {len(self.used_location_names) + 1}"

        name = random.choice(available_names)
        self.used_location_names.add(name)
        return name

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

    def auto_generate_from_genre(
        self,
        genre: str,
        name: Optional[str] = None,
        editable_config: Optional[Dict[str, Any]] = None
    ) -> tuple:
        """
        Auto-generate a complete world based on story genre with random entities.

        Args:
            genre: Story genre (adventure, mystery, conflict, discovery)
            name: Optional world name (auto-generated if not provided)
            editable_config: Optional configuration to override defaults
                - num_people: Number of people (default: random 3-15)
                - has_forests: Whether to include forests (default: random)
                - num_rivers: Number of rivers (default: random 0-5)
                - num_lakes: Number of lakes (default: random 0-3)
                - river_danger: Danger level of rivers 0-10 (default: random)
                - forest_danger: Danger level of forests 0-10 (default: random)
                - lake_danger: Danger level of lakes 0-10 (default: random)

        Returns:
            Tuple of (World, List[Location], List[Entity], Dict[config])
        """
        # Map genre to world type
        genre_to_world_type = {
            "adventure": "fantasy",
            "mystery": "modern",
            "conflict": "historical",
            "discovery": "sci-fi"
        }

        world_type = genre_to_world_type.get(genre, "fantasy")

        # Initialize editable configuration with random values
        config = editable_config or {}

        # Random number of people (3-15)
        num_people = config.get("num_people", random.randint(3, 15))

        # Random forest presence (70% chance)
        has_forests = config.get("has_forests", random.random() < 0.7)

        # Random number of rivers (0-5)
        num_rivers = config.get("num_rivers", random.randint(0, 5))

        # Random number of lakes (0-3)
        num_lakes = config.get("num_lakes", random.randint(0, 3))

        # Random danger levels (0-10)
        river_danger = config.get("river_danger", random.randint(0, 10))
        forest_danger = config.get("forest_danger", random.randint(0, 10))
        lake_danger = config.get("lake_danger", random.randint(0, 10))

        # Store final config for editing
        final_config = {
            "num_people": num_people,
            "has_forests": has_forests,
            "num_rivers": num_rivers,
            "num_lakes": num_lakes,
            "river_danger": river_danger,
            "forest_danger": forest_danger,
            "lake_danger": lake_danger,
            "genre": genre,
            "world_type": world_type
        }

        # Generate world name
        world_name = name or self._generate_name(world_type)

        # Create world description based on config
        description = f"A {world_type} world created for {genre} stories. "
        description += f"Population: {num_people} people. "
        if has_forests:
            description += f"Contains forests (danger level: {forest_danger}/10). "
        if num_rivers > 0:
            description += f"Has {num_rivers} river(s) (danger level: {river_danger}/10). "
        if num_lakes > 0:
            description += f"Has {num_lakes} lake(s) (danger level: {lake_danger}/10)."

        # Create world
        world = World(
            name=world_name,
            description=description,
            metadata={
                "world_type": world_type,
                "genre": genre,
                "auto_generated": True,
                **final_config
            }
        )

        # Generate locations
        locations = []

        # Add villages/settlements based on population
        num_settlements = max(1, num_people // 5)
        for i in range(num_settlements):
            settlement_type = random.choice(["village", "town", "settlement", "camp"])
            location = Location(
                name=f"{settlement_type.title()} {i + 1}",
                description=f"A {settlement_type} with approximately {num_people // num_settlements} inhabitants",
                world_id=world.world_id,
                coordinates={
                    "x": random.uniform(-1000, 1000),
                    "y": random.uniform(-1000, 1000),
                    "z": random.uniform(0, 100)
                },
                metadata={"location_type": settlement_type, "population": num_people // num_settlements}
            )
            locations.append(location)
            world.add_location(location.location_id)

        # Add forests if enabled
        if has_forests:
            num_forests = random.randint(1, 3)
            for i in range(num_forests):
                forest = Location(
                    name=f"Forest {i + 1}",
                    description=f"A forest area with danger level {forest_danger}/10",
                    world_id=world.world_id,
                    coordinates={
                        "x": random.uniform(-1000, 1000),
                        "y": random.uniform(-1000, 1000),
                        "z": random.uniform(0, 50)
                    },
                    metadata={"location_type": "forest", "danger_level": forest_danger}
                )
                locations.append(forest)
                world.add_location(forest.location_id)

        # Add rivers
        for i in range(num_rivers):
            river = Location(
                name=f"River {i + 1}",
                description=f"A river with danger level {river_danger}/10",
                world_id=world.world_id,
                coordinates={
                    "x": random.uniform(-1000, 1000),
                    "y": random.uniform(-1000, 1000),
                    "z": 0
                },
                metadata={"location_type": "river", "danger_level": river_danger}
            )
            locations.append(river)
            world.add_location(river.location_id)

        # Add lakes
        for i in range(num_lakes):
            lake = Location(
                name=f"Lake {i + 1}",
                description=f"A lake with danger level {lake_danger}/10",
                world_id=world.world_id,
                coordinates={
                    "x": random.uniform(-1000, 1000),
                    "y": random.uniform(-1000, 1000),
                    "z": 0
                },
                metadata={"location_type": "lake", "danger_level": lake_danger}
            )
            locations.append(lake)
            world.add_location(lake.location_id)

        # Generate entities (people and creatures)
        entities = []

        # Generate people entities
        if world_type in self.WORLD_TYPES:
            entity_types = self.WORLD_TYPES[world_type]["entity_types"]
        else:
            entity_types = ["character"]

        for i in range(num_people):
            entity_type = random.choice(entity_types)
            name = f"{entity_type.title()} {i + 1}"

            entity = Entity(
                name=name,
                entity_type=entity_type,
                description=f"A {entity_type} in {world.name}",
                world_id=world.world_id,
                attributes={
                    "strength": random.randint(1, 10),
                    "intelligence": random.randint(1, 10),
                    "charisma": random.randint(1, 10),
                    "is_dangerous": False
                }
            )
            entities.append(entity)
            world.add_entity(entity.entity_id)

        # Generate dangerous creatures based on danger levels
        total_danger = 0
        if has_forests:
            total_danger += forest_danger
        if num_rivers > 0:
            total_danger += river_danger
        if num_lakes > 0:
            total_danger += lake_danger

        # More dangerous areas = more dangerous creatures
        num_dangerous_creatures = total_danger // 3  # 1 creature per 3 danger points

        dangerous_creature_types = {
            "fantasy": ["dragon", "monster", "beast", "demon"],
            "sci-fi": ["alien predator", "rogue AI", "mutant", "hostile drone"],
            "modern": ["criminal", "wild animal", "aggressive dog"],
            "historical": ["bandit", "wild beast", "raider"]
        }

        creature_types = dangerous_creature_types.get(world_type, ["creature"])

        for i in range(num_dangerous_creatures):
            creature_type = random.choice(creature_types)
            name = f"Dangerous {creature_type.title()} {i + 1}"

            # Higher danger means stronger creatures
            # Calculate average danger only if there are dangerous areas
            num_dangerous_areas = int(has_forests) + int(num_rivers > 0) + int(num_lakes > 0)
            if num_dangerous_areas > 0 and total_danger > 0:
                avg_danger = total_danger / num_dangerous_areas
            else:
                avg_danger = 1  # Minimum danger if somehow we have creatures with no danger

            entity = Entity(
                name=name,
                entity_type=creature_type,
                description=f"A dangerous {creature_type} in {world.name}",
                world_id=world.world_id,
                attributes={
                    "strength": int(avg_danger),
                    "intelligence": random.randint(1, 5),
                    "charisma": random.randint(1, 3),
                    "is_dangerous": True,
                    "threat_level": int(avg_danger)
                }
            )
            entities.append(entity)
            world.add_entity(entity.entity_id)

        return world, locations, entities, final_config
