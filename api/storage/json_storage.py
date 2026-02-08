"""Storage utilities for managing JSON files."""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class Storage:
    """Handles storage and retrieval of worlds, stories, and related data."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize Storage.

        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = Path(data_dir)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure all necessary directories exist."""
        directories = [
            self.data_dir,
            self.data_dir / "worlds",
            self.data_dir / "stories",
            self.data_dir / "locations",
            self.data_dir / "entities",
            self.data_dir / "time_cones"
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def save_world(self, world_data: Dict[str, Any]) -> str:
        """
        Save a world to a JSON file.

        Args:
            world_data: World data dictionary

        Returns:
            Path to the saved file
        """
        world_id = world_data["world_id"]
        file_path = self.data_dir / "worlds" / f"{world_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(world_data, f, indent=2, ensure_ascii=False)

        return str(file_path)

    def load_world(self, world_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a world from a JSON file.

        Args:
            world_id: World ID

        Returns:
            World data dictionary or None if not found
        """
        file_path = self.data_dir / "worlds" / f"{world_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_worlds(self) -> List[Dict[str, Any]]:
        """
        List all worlds.

        Returns:
            List of world data dictionaries
        """
        worlds = []
        worlds_dir = self.data_dir / "worlds"

        for file_path in worlds_dir.glob("*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                worlds.append(json.load(f))

        return worlds

    def save_story(self, story_data: Dict[str, Any]) -> str:
        """
        Save a story to a JSON file.

        Args:
            story_data: Story data dictionary

        Returns:
            Path to the saved file
        """
        story_id = story_data["story_id"]
        file_path = self.data_dir / "stories" / f"{story_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(story_data, f, indent=2, ensure_ascii=False)

        return str(file_path)

    def load_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a story from a JSON file.

        Args:
            story_id: Story ID

        Returns:
            Story data dictionary or None if not found
        """
        file_path = self.data_dir / "stories" / f"{story_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_stories(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all stories, optionally filtered by world.

        Args:
            world_id: Optional world ID to filter by

        Returns:
            List of story data dictionaries
        """
        stories = []
        stories_dir = self.data_dir / "stories"

        for file_path in stories_dir.glob("*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                story = json.load(f)
                if world_id is None or story.get("world_id") == world_id:
                    stories.append(story)

        return stories

    def save_location(self, location_data: Dict[str, Any]) -> str:
        """
        Save a location to a JSON file.

        Args:
            location_data: Location data dictionary

        Returns:
            Path to the saved file
        """
        location_id = location_data["location_id"]
        file_path = self.data_dir / "locations" / f"{location_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(location_data, f, indent=2, ensure_ascii=False)

        return str(file_path)

    def load_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a location from a JSON file.

        Args:
            location_id: Location ID

        Returns:
            Location data dictionary or None if not found
        """
        file_path = self.data_dir / "locations" / f"{location_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_locations(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all locations, optionally filtered by world.

        Args:
            world_id: Optional world ID to filter by

        Returns:
            List of location data dictionaries
        """
        locations = []
        locations_dir = self.data_dir / "locations"

        for file_path in locations_dir.glob("*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                location = json.load(f)
                if world_id is None or location.get("world_id") == world_id:
                    locations.append(location)

        return locations

    def load_all_locations(self) -> List[Dict[str, Any]]:
        """
        Load all locations from storage.

        Returns:
            List of all location data dictionaries
        """
        return self.list_locations()

    def delete_location(self, location_id: str) -> bool:
        """
        Delete a location file.

        Args:
            location_id: Location ID

        Returns:
            True if deleted, False if not found
        """
        file_path = self.data_dir / "locations" / f"{location_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def save_entity(self, entity_data: Dict[str, Any]) -> str:
        """
        Save an entity to a JSON file.

        Args:
            entity_data: Entity data dictionary

        Returns:
            Path to the saved file
        """
        entity_id = entity_data["entity_id"]
        file_path = self.data_dir / "entities" / f"{entity_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entity_data, f, indent=2, ensure_ascii=False)

        return str(file_path)

    def load_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Load an entity from a JSON file.

        Args:
            entity_id: Entity ID

        Returns:
            Entity data dictionary or None if not found
        """
        file_path = self.data_dir / "entities" / f"{entity_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_entities(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all entities, optionally filtered by world.

        Args:
            world_id: Optional world ID to filter by

        Returns:
            List of entity data dictionaries
        """
        entities = []
        entities_dir = self.data_dir / "entities"

        for file_path in entities_dir.glob("*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                entity = json.load(f)
                if world_id is None or entity.get("world_id") == world_id:
                    entities.append(entity)

        return entities

    def load_all_entities(self) -> List[Dict[str, Any]]:
        """
        Load all entities from storage.

        Returns:
            List of all entity data dictionaries
        """
        return self.list_entities()

    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity file.

        Args:
            entity_id: Entity ID

        Returns:
            True if deleted, False if not found
        """
        file_path = self.data_dir / "entities" / f"{entity_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def save_time_cone(self, time_cone_data: Dict[str, Any]) -> str:
        """
        Save a time cone to a JSON file.

        Args:
            time_cone_data: Time cone data dictionary

        Returns:
            Path to the saved file
        """
        time_cone_id = time_cone_data["time_cone_id"]
        file_path = self.data_dir / "time_cones" / f"{time_cone_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(time_cone_data, f, indent=2, ensure_ascii=False)

        return str(file_path)

    def load_time_cone(self, time_cone_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a time cone from a JSON file.

        Args:
            time_cone_id: Time cone ID

        Returns:
            Time cone data dictionary or None if not found
        """
        file_path = self.data_dir / "time_cones" / f"{time_cone_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def delete_world(self, world_id: str) -> bool:
        """
        Delete a world file.

        Args:
            world_id: World ID

        Returns:
            True if deleted, False if not found
        """
        file_path = self.data_dir / "worlds" / f"{world_id}.json"

        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def delete_story(self, story_id: str) -> bool:
        """
        Delete a story file.

        Args:
            story_id: Story ID

        Returns:
            True if deleted, False if not found
        """
        file_path = self.data_dir / "stories" / f"{story_id}.json"

        if file_path.exists():
            file_path.unlink()
            return True
        return False
