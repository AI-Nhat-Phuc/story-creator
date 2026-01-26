"""Story linker for connecting stories within a world."""

from typing import List, Dict, Any, Set
from core.models import Story


class StoryLinker:
    """Links multiple stories together within the same world using logical algorithms."""

    def __init__(self):
        """Initialize the StoryLinker."""
        pass

    def link_by_entities(self, stories: List[Story]) -> Dict[str, List[str]]:
        """
        Link stories that share entities.

        Args:
            stories: List of Story objects

        Returns:
            Dictionary mapping story IDs to lists of linked story IDs
        """
        links = {story.story_id: [] for story in stories}

        # Build entity to stories mapping
        entity_stories: Dict[str, List[str]] = {}
        for story in stories:
            for entity_id in story.entities:
                if entity_id not in entity_stories:
                    entity_stories[entity_id] = []
                entity_stories[entity_id].append(story.story_id)

        # Create links between stories sharing entities
        for story in stories:
            linked_story_ids: Set[str] = set()

            for entity_id in story.entities:
                # Find other stories with this entity
                for other_story_id in entity_stories[entity_id]:
                    if other_story_id != story.story_id:
                        linked_story_ids.add(other_story_id)

            links[story.story_id] = list(linked_story_ids)

        return links

    def link_by_locations(self, stories: List[Story]) -> Dict[str, List[str]]:
        """
        Link stories that share locations.

        Args:
            stories: List of Story objects

        Returns:
            Dictionary mapping story IDs to lists of linked story IDs
        """
        links = {story.story_id: [] for story in stories}

        # Build location to stories mapping
        location_stories: Dict[str, List[str]] = {}
        for story in stories:
            for location_id in story.locations:
                if location_id not in location_stories:
                    location_stories[location_id] = []
                location_stories[location_id].append(story.story_id)

        # Create links between stories sharing locations
        for story in stories:
            linked_story_ids: Set[str] = set()

            for location_id in story.locations:
                # Find other stories at this location
                for other_story_id in location_stories[location_id]:
                    if other_story_id != story.story_id:
                        linked_story_ids.add(other_story_id)

            links[story.story_id] = list(linked_story_ids)

        return links

    def link_by_time_cones(self, stories: List[Story]) -> Dict[str, List[str]]:
        """
        Link stories that share temporal context (time cones).

        Args:
            stories: List of Story objects

        Returns:
            Dictionary mapping story IDs to lists of linked story IDs
        """
        links = {story.story_id: [] for story in stories}

        # Build time cone to stories mapping
        time_cone_stories: Dict[str, List[str]] = {}
        for story in stories:
            for time_cone_id in story.time_cones:
                if time_cone_id not in time_cone_stories:
                    time_cone_stories[time_cone_id] = []
                time_cone_stories[time_cone_id].append(story.story_id)

        # Create links between stories sharing time cones
        for story in stories:
            linked_story_ids: Set[str] = set()

            for time_cone_id in story.time_cones:
                # Find other stories in this time cone
                for other_story_id in time_cone_stories[time_cone_id]:
                    if other_story_id != story.story_id:
                        linked_story_ids.add(other_story_id)

            links[story.story_id] = list(linked_story_ids)

        return links

    def link_stories(
        self,
        stories: List[Story],
        link_by_entities: bool = True,
        link_by_locations: bool = True,
        link_by_time: bool = True
    ) -> None:
        """
        Link stories together using multiple criteria.

        Args:
            stories: List of Story objects to link
            link_by_entities: Whether to link by shared entities
            link_by_locations: Whether to link by shared locations
            link_by_time: Whether to link by shared time cones
        """
        all_links: Dict[str, Set[str]] = {story.story_id: set() for story in stories}

        # Collect links from different criteria
        if link_by_entities:
            entity_links = self.link_by_entities(stories)
            for story_id, linked_ids in entity_links.items():
                all_links[story_id].update(linked_ids)

        if link_by_locations:
            location_links = self.link_by_locations(stories)
            for story_id, linked_ids in location_links.items():
                all_links[story_id].update(linked_ids)

        if link_by_time:
            time_links = self.link_by_time_cones(stories)
            for story_id, linked_ids in time_links.items():
                all_links[story_id].update(linked_ids)

        # Apply links to stories
        story_map = {story.story_id: story for story in stories}

        for story_id, linked_ids in all_links.items():
            if story_id in story_map:
                story = story_map[story_id]
                for linked_id in linked_ids:
                    story.link_story(linked_id)

    def get_story_graph(self, stories: List[Story]) -> Dict[str, Any]:
        """
        Get a graph representation of story links.

        Args:
            stories: List of Story objects

        Returns:
            Graph data structure with nodes and edges
        """
        nodes = []
        edges = []

        for story in stories:
            nodes.append({
                "id": story.story_id,
                "title": story.title,
                "world_id": story.world_id
            })

            for linked_story_id in story.linked_stories:
                edges.append({
                    "from": story.story_id,
                    "to": linked_story_id
                })

        return {
            "nodes": nodes,
            "edges": edges
        }
