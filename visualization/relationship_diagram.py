"""Relationship diagram visualization for Story Creator.

This module provides relationship diagram generation for characters/entities,
including layout algorithms and connection analysis.
"""

import math
import logging
from typing import Dict, List, Tuple, Set, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NodePosition:
    """Position of a node in the diagram."""
    entity_id: str
    x: float
    y: float
    name: str
    entity_type: str
    color: str


@dataclass
class Connection:
    """Connection between two nodes."""
    entity1_id: str
    entity2_id: str
    connection_type: str  # "story", "location", "story+location"
    color: str
    width: int


class RelationshipDiagram:
    """Generate relationship diagrams for entities in a world."""

    # Color scheme
    COLORS = {
        'character': '#3498DB',      # Blue
        'dangerous': '#E74C3C',      # Red
        'object': '#2ECC71',         # Green
        'connection_story': '#4ECDC4',
        'connection_both': '#FF6B6B',
        'outline': '#2C3E50'
    }

    def __init__(self, canvas_width: int = 1200, canvas_height: int = 800):
        """
        Initialize relationship diagram generator.

        Args:
            canvas_width: Width of the canvas
            canvas_height: Height of the canvas
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.center_x = canvas_width // 2
        self.center_y = canvas_height // 2
        logger.debug(f"RelationshipDiagram initialized: {canvas_width}x{canvas_height}")

    def analyze_connections(
        self,
        stories: List[Dict[str, Any]],
        world_locations: List[str]
    ) -> Dict[str, Dict[str, str]]:
        """
        Analyze entity connections from stories.

        Args:
            stories: List of story data dictionaries
            world_locations: List of location IDs in the world

        Returns:
            Dictionary mapping entity_id to connected entities with connection types
            {entity_id: {connected_entity_id: connection_type}}
        """
        entity_connections = {}

        # Analyze story connections
        for story_data in stories:
            story_entities = story_data.get('entities', [])
            # Entities in same story are connected
            for i, ent1_id in enumerate(story_entities):
                for ent2_id in story_entities[i+1:]:
                    if ent1_id not in entity_connections:
                        entity_connections[ent1_id] = {}
                    if ent2_id not in entity_connections:
                        entity_connections[ent2_id] = {}

                    # Mark bidirectional connection
                    entity_connections[ent1_id][ent2_id] = "story"
                    entity_connections[ent2_id][ent1_id] = "story"

        # Analyze location connections
        for story_data in stories:
            story_locs = story_data.get('locations', [])
            story_ents = story_data.get('entities', [])
            if story_locs and len(story_ents) > 1:
                # Multiple entities at same location
                for i, ent1_id in enumerate(story_ents):
                    for ent2_id in story_ents[i+1:]:
                        if ent1_id in entity_connections and ent2_id in entity_connections[ent1_id]:
                            # Already connected by story, mark location too
                            entity_connections[ent1_id][ent2_id] = "story+location"
                            entity_connections[ent2_id][ent1_id] = "story+location"

        logger.info(f"Analyzed {len(entity_connections)} entity connections from {len(stories)} stories")
        return entity_connections

    def get_entity_color(self, entity_type: str) -> str:
        """
        Get color for entity based on type.

        Args:
            entity_type: Entity type string

        Returns:
            Hex color code
        """
        entity_type_lower = entity_type.lower()
        if "character" in entity_type_lower or "person" in entity_type_lower or "người" in entity_type_lower:
            return self.COLORS['character']
        elif "dangerous" in entity_type_lower or "creature" in entity_type_lower or "sinh vật" in entity_type_lower:
            return self.COLORS['dangerous']
        else:
            return self.COLORS['object']

    def circular_layout(
        self,
        entities: List[Any],
        radius: Optional[int] = None
    ) -> Dict[str, Tuple[float, float]]:
        """
        Calculate circular layout positions for entities.

        Args:
            entities: List of entity objects with entity_id attribute
            radius: Radius of the circle (defaults to 1/3 of min canvas dimension)

        Returns:
            Dictionary mapping entity_id to (x, y) coordinates
        """
        if radius is None:
            radius = min(self.canvas_width, self.canvas_height) // 3

        num_entities = len(entities)
        positions = {}

        for i, entity in enumerate(entities):
            angle = 2 * math.pi * i / num_entities
            x = self.center_x + radius * math.cos(angle)
            y = self.center_y + radius * math.sin(angle)
            positions[entity.entity_id] = (x, y)

        return positions

    def force_directed_layout(
        self,
        entities: List[Any],
        connections: Dict[str, Dict[str, str]],
        iterations: int = 100
    ) -> Dict[str, Tuple[float, float]]:
        """
        Calculate force-directed layout positions (Fruchterman-Reingold algorithm).

        Args:
            entities: List of entity objects
            connections: Connection dictionary from analyze_connections
            iterations: Number of iterations for the algorithm

        Returns:
            Dictionary mapping entity_id to (x, y) coordinates
        """
        # Start with random positions
        import random
        positions = {}
        margin = 100
        for entity in entities:
            x = random.uniform(margin, self.canvas_width - margin)
            y = random.uniform(margin, self.canvas_height - margin)
            positions[entity.entity_id] = [x, y]

        # Algorithm parameters
        area = self.canvas_width * self.canvas_height
        k = math.sqrt(area / len(entities))  # Optimal distance
        temperature = self.canvas_width / 10

        for iteration in range(iterations):
            # Calculate repulsive forces between all nodes
            displacements = {ent.entity_id: [0.0, 0.0] for ent in entities}

            # Repulsion between all pairs
            for i, ent1 in enumerate(entities):
                for ent2 in entities[i+1:]:
                    pos1 = positions[ent1.entity_id]
                    pos2 = positions[ent2.entity_id]

                    dx = pos1[0] - pos2[0]
                    dy = pos1[1] - pos2[1]
                    distance = math.sqrt(dx*dx + dy*dy) or 1

                    # Repulsive force
                    force = k * k / distance
                    displacements[ent1.entity_id][0] += (dx / distance) * force
                    displacements[ent1.entity_id][1] += (dy / distance) * force
                    displacements[ent2.entity_id][0] -= (dx / distance) * force
                    displacements[ent2.entity_id][1] -= (dy / distance) * force

            # Calculate attractive forces for connected nodes
            for ent1_id, connected in connections.items():
                if ent1_id not in positions:
                    continue
                for ent2_id in connected.keys():
                    if ent2_id not in positions:
                        continue

                    pos1 = positions[ent1_id]
                    pos2 = positions[ent2_id]

                    dx = pos1[0] - pos2[0]
                    dy = pos1[1] - pos2[1]
                    distance = math.sqrt(dx*dx + dy*dy) or 1

                    # Attractive force
                    force = distance * distance / k
                    displacements[ent1_id][0] -= (dx / distance) * force
                    displacements[ent1_id][1] -= (dy / distance) * force

            # Apply displacements with temperature
            for entity in entities:
                ent_id = entity.entity_id
                dx, dy = displacements[ent_id]
                displacement = math.sqrt(dx*dx + dy*dy) or 1

                # Limit displacement by temperature
                positions[ent_id][0] += (dx / displacement) * min(displacement, temperature)
                positions[ent_id][1] += (dy / displacement) * min(displacement, temperature)

                # Keep within bounds
                positions[ent_id][0] = max(margin, min(self.canvas_width - margin, positions[ent_id][0]))
                positions[ent_id][1] = max(margin, min(self.canvas_height - margin, positions[ent_id][1]))

            # Cool down
            temperature *= 0.95

        # Convert to tuples
        return {ent_id: tuple(pos) for ent_id, pos in positions.items()}

    def generate_node_positions(
        self,
        entities: List[Any],
        layout: str = "circular",
        connections: Optional[Dict[str, Dict[str, str]]] = None
    ) -> List[NodePosition]:
        """
        Generate node positions for entities.

        Args:
            entities: List of entity objects
            layout: Layout algorithm ("circular" or "force-directed")
            connections: Connection dictionary (required for force-directed layout)

        Returns:
            List of NodePosition objects
        """
        if layout == "force-directed" and connections:
            positions = self.force_directed_layout(entities, connections)
        else:
            positions = self.circular_layout(entities)

        node_positions = []
        for entity in entities:
            if entity.entity_id not in positions:
                continue

            x, y = positions[entity.entity_id]
            color = self.get_entity_color(entity.entity_type)

            node_positions.append(NodePosition(
                entity_id=entity.entity_id,
                x=x,
                y=y,
                name=entity.name,
                entity_type=entity.entity_type,
                color=color
            ))

        return node_positions

    def generate_connections(
        self,
        entity_connections: Dict[str, Dict[str, str]],
        positions: Dict[str, Tuple[float, float]]
    ) -> List[Connection]:
        """
        Generate connection objects for drawing.

        Args:
            entity_connections: Connection dictionary from analyze_connections
            positions: Position dictionary mapping entity_id to (x, y)

        Returns:
            List of Connection objects
        """
        connections = []
        drawn_connections = set()

        for ent1_id, connected in entity_connections.items():
            for ent2_id, conn_type in connected.items():
                # Avoid drawing same connection twice
                conn_key = tuple(sorted([ent1_id, ent2_id]))
                if conn_key in drawn_connections:
                    continue
                drawn_connections.add(conn_key)

                if ent1_id not in positions or ent2_id not in positions:
                    continue

                # Different styles for different connection types
                if conn_type == "story+location":
                    color = self.COLORS['connection_both']
                    width = 3
                else:
                    color = self.COLORS['connection_story']
                    width = 2

                connections.append(Connection(
                    entity1_id=ent1_id,
                    entity2_id=ent2_id,
                    connection_type=conn_type,
                    color=color,
                    width=width
                ))

        return connections

    def get_diagram_stats(
        self,
        world_name: str,
        num_entities: int,
        num_connections: int
    ) -> str:
        """
        Generate statistics string for the diagram.

        Args:
            world_name: Name of the world
            num_entities: Number of entities
            num_connections: Number of connections

        Returns:
            Formatted statistics string
        """
        return f"🌍 {world_name} | 👥 {num_entities} nhân vật | 🔗 {num_connections} mối quan hệ"
