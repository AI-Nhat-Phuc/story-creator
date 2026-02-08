"""Character service for managing character linking and detection."""

from typing import List, Tuple


class CharacterService:
    """Service for handling character-related operations."""

    @staticmethod
    def detect_mentioned_characters(
        description: str,
        entity_data_list: List[dict]
    ) -> Tuple[List[str], List[str]]:
        """
        Detect which characters are mentioned in the description.

        Args:
            description: Story description text
            entity_data_list: List of entity dictionaries with 'name' and 'entity_id'

        Returns:
            Tuple of (character_names, entity_ids)
        """
        mentioned_names = []
        mentioned_ids = []

        for entity_data in entity_data_list:
            if entity_data['name'] in description:
                mentioned_names.append(entity_data['name'])
                mentioned_ids.append(entity_data['entity_id'])

        return mentioned_names, mentioned_ids

    @staticmethod
    def get_character_names(entity_data_list: List[dict], exclude_dangerous: bool = True) -> List[str]:
        """
        Extract character names from entity data.

        Args:
            entity_data_list: List of entity dictionaries
            exclude_dangerous: Whether to exclude dangerous creatures

        Returns:
            List of character names
        """
        names = []
        for entity_data in entity_data_list:
            if exclude_dangerous and 'Dangerous' in entity_data['name']:
                continue
            names.append(entity_data['name'])

        return names

    @staticmethod
    def format_character_display(entity_data: dict) -> str:
        """
        Format character data for display.

        Args:
            entity_data: Entity dictionary with 'name' and 'entity_type'

        Returns:
            Formatted display string
        """
        return f"👤 {entity_data['name']} ({entity_data['entity_type']})"

    @staticmethod
    def add_character_info_to_description(description: str, mentioned_names: List[str]) -> str:
        """
        Add character information section to description.

        Args:
            description: Original description
            mentioned_names: List of mentioned character names

        Returns:
            Description with character info appended
        """
        if not mentioned_names:
            return description

        description += f"\n\n--- Nhân vật liên quan ---\n"
        description += f"Câu chuyện này đề cập đến: {', '.join(mentioned_names)}"

        return description
