"""GPT prompt templates for Story Creator AI features."""

from typing import Dict, List, Any


class PromptTemplates:
    """Centralized prompt templates for GPT interactions."""

    # ===== COMMON SETTINGS =====
    OUTPUT_LANGUAGE = "Vietnamese"
    OUTPUT_LANGUAGE_INSTRUCTION = "Always respond in Vietnamese."

    # Story templates by genre (dùng cho prompt tạo mô tả tự động)
    STORY_TEMPLATES = {
        "ADVENTURE": [
            "A journey to {location} where {entity} discovers {element}",
            "{entity} embarks on a quest to find {element} in {location}",
            "An unexpected adventure leads {entity} to {location}"
        ],
        "MYSTERY": [
            "A strange occurrence in {location} draws {entity} into investigation",
            "{entity} uncovers secrets about {element} in {location}",
            "The mystery of {location} challenges {entity}"
        ],
        "CONFLICT": [
            "{entity} faces a great challenge in {location}",
            "A battle for {element} unfolds in {location}",
            "{entity} must defend {location} against threats"
        ],
        "DISCOVERY": [
            "{entity} makes a groundbreaking discovery in {location}",
            "Hidden knowledge about {element} is revealed to {entity}",
            "An ancient secret in {location} changes everything for {entity}"
        ]
    }

    # ===== SYSTEM PROMPTS =====
    TRANSLATOR_SYSTEM = (
        "You are a professional English to Vietnamese translator. "
        "Translate the given text accurately while preserving the tone and style."
    )

    CHARACTER_DECISION_SYSTEM = (
        "You are {character_name}, a character with these traits: {traits}. "
        "Make decisions based on your character's personality and attributes."
    )

    STORYTELLER_SYSTEM = (
        "You are a creative storyteller. Based on the story and character decisions, "
        "predict what happens next in 2-3 sentences."
    )

    CHOICE_GENERATOR_SYSTEM = (
        "Generate exactly 3 choices for a story situation: "
        "Choice A (action), Choice B (opposing action), Choice C (abandon/retreat). "
        "Keep each choice to one sentence."
    )

    WORLD_DESCRIPTION_SYSTEM = (
        "You are a creative world-building expert. Generate vivid, detailed descriptions "
        "for fictional worlds based on their type and characteristics."
    )

    STORY_DESCRIPTION_SYSTEM = (
        "You are a professional storyteller. Create engaging story descriptions "
        "that capture the essence of the narrative."
    )

    # ===== GPT SERVICE SYSTEM PROMPTS =====
    WORLD_GENERATOR_SYSTEM = (
        "You are a creative world-building assistant. "
        + OUTPUT_LANGUAGE_INSTRUCTION + " "
        "Return only the description content, no titles or explanations."
    )

    STORY_GENERATOR_SYSTEM = (
        "You are a creative storytelling assistant. "
        + OUTPUT_LANGUAGE_INSTRUCTION + " "
        "Return only the story content, no titles or explanations."
    )

    TEXT_ANALYZER_SYSTEM = (
        "You are a text analysis assistant. "
        "Return only pure JSON, no additional text or explanations."
    )

    # ===== API BACKEND PROMPTS =====
    API_WORLD_GENERATOR_SYSTEM = (
        "You are a creative world-building assistant. "
        + OUTPUT_LANGUAGE_INSTRUCTION + " "
        "Return only the description content, no titles, notes or explanations."
    )

    API_STORY_GENERATOR_SYSTEM = (
        "You are a creative storytelling assistant. "
        + OUTPUT_LANGUAGE_INSTRUCTION + " "
        "Return only the story content, no titles, notes or explanations."
    )

    API_WORLD_DESCRIPTION_TEMPLATE = """Create a detailed description for a {world_type} world named '{world_name}'.

Requirements:
- Include: general background, geographical features, culture, society and unique elements
- Length: approximately 150-200 words
- Natural and vivid writing style

Return ONLY the world description content, NO titles, notes, explanations or any other text."""

    API_STORY_DESCRIPTION_TEMPLATE = """Create a description for a {story_genre} story titled '{story_title}'.
{context}
Requirements:
- Include: initial situation, character goals, challenges to overcome
- Length: approximately 100-150 words
- Engaging and inspiring storytelling style

Return ONLY the story description content, NO titles, notes, explanations or any other text."""

    # ===== USER PROMPT TEMPLATES =====
    WORLD_DESCRIPTION_TEMPLATE = """Create a detailed description for a {world_type} world.
The description should be vivid, engaging, and suitable for storytelling context.
Include details about the environment, atmosphere, and key characteristics.
Length: 100-200 words.

RULE: Return ONLY the description content, NO titles, explanations, or notes."""

    STORY_DESCRIPTION_WITH_BASE_TEMPLATE = """The user has written the following story idea: "{base_description}"

Expand and develop this idea into an engaging {genre} story in a {world_type} world.
KEEP THE ORIGINAL IDEA but add details, emotions, and context.
World description: {world_description}

The story should be creative, engaging, and appropriate for the genre.
Clearly identify the main character from the beginning.
Length: 80-150 words.

RULE: Return ONLY the story content, NO titles, explanations, or notes."""

    STORY_DESCRIPTION_NEW_TEMPLATE = """Create an engaging {genre} story in a {world_type} world.
World description: {world_description}

The story should be creative, engaging, and appropriate for the genre.
Clearly identify the main character from the beginning.
Length: 80-150 words.

RULE: Return ONLY the story content, NO titles, explanations, or notes."""

    ANALYZE_WORLD_ENTITIES_TEMPLATE = """You are a text analysis assistant. ANALYZE the following world description and ONLY EXTRACT characters and locations that ARE MENTIONED:

World description: {world_description}
World type: {world_type}

TASK: ONLY identify and extract information from the description, DO NOT create anything new

ANALYSIS REQUIREMENTS:
1. CHARACTERS:
   - ONLY list characters that ARE MENTIONED in the description
   - Identify type (entity_type) in Vietnamese
   - IF no characters are mentioned → return empty array []
   - ALL description text MUST be in Vietnamese

2. LOCATIONS:
   - ONLY list locations that ARE MENTIONED in the description
   - IF no locations are mentioned → return empty array []
   - ALL description text MUST be in Vietnamese

Return JSON with structure:
{{
  "entities": [
    {{
      "name": "Character NAME from description",
      "entity_type": "Loai thực thể bằng tiếng Việt (nhân vật chính/nhân vật phụ/sinh vật nguy hiểm/...)",
      "description": "Mô tả bằng tiếng Việt dựa trên thông tin CÓ SẴN trong văn bản (10-20 từ)",
      "attributes": {{"Tên": number_0_10, "Trí tuệ": number_0_10, "Sức hấp dẫn": number_0_10}}
    }}
  ],
  "locations": [
    {{
      "name": "Location NAME from description",
      "description": "Mô tả bằng tiếng Việt dựa trên thông tin CÓ SẴN (10-20 từ)",
      "coordinates": {{"x": random_number_0_100, "y": random_number_0_100}}
    }}
  ]
}}

MANDATORY RULES:
✅ ONLY extract information that EXISTS in the description, DO NOT create new content
✅ IF no characters/locations found → return empty array []
✅ DESCRIPTION must be based on existing information, no fictional details
✅ Keep proper names as-is
✅ entity_type and description MUST be in Vietnamese
✅ Estimate attributes based on description (if unclear → average value 5)
✅ Return only valid JSON, NO additional explanations"""

    ANALYZE_STORY_ENTITIES_TEMPLATE = """You are a text analysis assistant. ANALYZE the following story description and ONLY EXTRACT characters and locations that ARE MENTIONED:

Title: {story_title}
Genre: {story_genre}
Story description: {story_description}

TASK: ONLY identify and extract information from the story description, DO NOT create anything new

ANALYSIS REQUIREMENTS:
1. CHARACTERS:
   - ONLY list characters that ARE MENTIONED in the story
   - Identify their role in the story (in Vietnamese)
   - IF no characters are mentioned → return empty array []

2. LOCATIONS:
   - ONLY list locations that ARE MENTIONED in the story
   - IF no locations are mentioned → return empty array []

Return JSON with structure:
{{
  "characters": [
    {{
      "name": "Character NAME from story",
      "role": "Vai trò trong câu chuyện bằng tiếng Việt (nhân vật chính/nhân vật phụ/phản diện/...)"
    }}
  ],
  "locations": [
    {{
      "name": "Location NAME from story",
      "description": "Mô tả ngắn bằng tiếng Việt (nếu có trong văn bản)"
    }}
  ]
}}

MANDATORY RULES:
✅ ONLY extract information that EXISTS in the story description, DO NOT create new content
✅ IF no characters/locations found → return empty array []
✅ Keep names exactly as they appear in the text
✅ All role and description text MUST be in Vietnamese
✅ Return only valid JSON, NO additional explanations"""

    BATCH_ANALYZE_STORY_ENTITIES_TEMPLATE = """You are a text analysis assistant. ANALYZE the following story description and ONLY EXTRACT characters and locations that ARE MENTIONED.

Title: {story_title}
Genre: {story_genre}
Story description: {story_description}

KNOWN CHARACTERS from earlier stories in this world (use exact names if the same character appears):
{known_characters}

KNOWN LOCATIONS from earlier stories in this world (use exact names if the same location appears):
{known_locations}

TASK: ONLY identify and extract information from the story description, DO NOT create anything new.
If a character or location from the KNOWN lists appears in this story, use the EXACT SAME NAME from the known list.

ANALYSIS REQUIREMENTS:
1. CHARACTERS:
   - ONLY list characters that ARE MENTIONED in the story
   - If a character matches a known character, use the known name exactly
   - Identify their role in the story (in Vietnamese)
   - IF no characters are mentioned → return empty array []

2. LOCATIONS:
   - ONLY list locations that ARE MENTIONED in the story
   - If a location matches a known location, use the known name exactly
   - IF no locations are mentioned → return empty array []

Return JSON with structure:
{{
  "characters": [
    {{
      "name": "Character NAME from story",
      "role": "Vai trò trong câu chuyện bằng tiếng Việt (nhân vật chính/nhân vật phụ/phản diện/...)"
    }}
  ],
  "locations": [
    {{
      "name": "Location NAME from story",
      "description": "Mô tả ngắn bằng tiếng Việt (nếu có trong văn bản)"
    }}
  ]
}}

MANDATORY RULES:
✅ ONLY extract information that EXISTS in the story description, DO NOT create new content
✅ IF no characters/locations found → return empty array []
✅ If character/location matches a known one, use the EXACT known name
✅ Keep names exactly as they appear in the text
✅ All role and description text MUST be in Vietnamese
✅ Return only valid JSON, NO additional explanations"""

    # ===== EVENT EXTRACTION PROMPTS =====

    EXTRACT_EVENTS_SYSTEM = (
        "You are a story analyst specializing in narrative event extraction. "
        "Extract key events from story content, identify temporal placement, "
        "involved characters and locations, and connections between events. "
        + OUTPUT_LANGUAGE_INSTRUCTION
    )

    EXTRACT_WORLD_EVENTS_SYSTEM = (
        "You are a professional event analysis assistant. Always return valid JSON. "
        + OUTPUT_LANGUAGE_INSTRUCTION
    )

    EXTRACT_WORLD_EVENTS_TEMPLATE = """You are a professional literary analyst. TASK: Extract important EVENTS from ALL the following stories in the same world.

STORY LIST:
{story_list}

STORY CONTENT (with line numbers):
{combined_content}

RULES:
1. Each event MUST be associated with a STORY_INDEX (0, 1, 2, ...) of the story containing it
2. story_position is the LINE NUMBER (the number before the | delimiter) in that story
3. Only extract events from paragraphs with ACTUAL CONTENT (not empty lines)
4. Create connections between events WITHIN and ACROSS stories
5. Do not create events with empty paragraph positions

KNOWN CHARACTERS: {known_characters}
KNOWN LOCATIONS: {known_locations}
CALENDAR: {calendar_info}

Return JSON in this format (all title, description, era, relation_label values MUST be in Vietnamese):
{{
  "events": [
    {{
      "story_index": 0,
      "title": "Tên sự kiện",
      "description": "Mô tả",
      "year": 1200,
      "era": "Kỷ nguyên ABC",
      "characters": ["Tên nhân vật"],
      "locations": ["Tên địa điểm"],
      "story_position": 5,
      "abstract_image_seed": "mô tả hình ảnh trừu tượng bằng tiếng Việt"
    }}
  ],
  "connections": [
    {{
      "from_event_index": 0,
      "to_event_index": 1,
      "relation_type": "causal",
      "relation_label": "Dẫn đến"
    }}
  ]
}}"""

    EXTRACT_EVENTS_TEMPLATE = """Analyze the following story and extract the main events.

Title: {story_title}
Genre: {story_genre}
Story content (each line is numbered at the beginning, empty lines also have numbers):
{story_content_numbered}

World information:
- Known characters: {known_characters}
- Known locations: {known_locations}
- Calendar system: {calendar_info}

Return JSON in the following format (all title, description, era, relation_label values MUST be in Vietnamese):
{{
    "events": [
        {{
            "title": "Tên sự kiện ngắn gọn (3-8 từ)",
            "description": "Mô tả ngắn 1-2 câu về sự kiện",
            "year": <integer, year in the world timeline, inferred from story context>,
            "era": "Kỷ nguyên (if available, from context)",
            "characters": ["character name 1", "character name 2"],
            "locations": ["location name"],
            "story_position": <paragraph index in content, starting from 0>,
            "abstract_image_seed": "2-3 English keywords describing an abstract image for the event"
        }}
    ],
    "connections": [
        {{
            "from_event_index": 0,
            "to_event_index": 1,
            "relation_type": "character|location|causation|temporal",
            "relation_label": "Mô tả ngắn mối liên kết"
        }}
    ]
}}

MANDATORY RULES:
✅ ONLY extract events that ACTUALLY EXIST in the content, DO NOT fabricate
✅ Each event must have at least 1 character OR 1 location
✅ year must be an integer, estimated based on story context
✅ story_position is the LINE NUMBER at the beginning of the line (the number before the | delimiter). Use this exact number, DO NOT recount. ONLY select lines with content (not empty lines).
✅ abstract_image_seed: use short English keywords (fire, battle, discovery, forest...)
✅ relation_type has only 4 types: character, location, causation, temporal
✅ DO NOT create events for empty paragraphs or paragraphs containing only whitespace
✅ DO NOT use world name as a location — only use specific places within the world
✅ DO NOT create "location" connections if the only reason is sharing the same world — only connect when sharing a specific location
✅ Return valid JSON, NO additional explanations"""

    # User prompts
    @staticmethod
    def translation_prompt(text: str) -> str:
        """Create translation prompt."""
        return f"Translate this to Vietnamese:\n\n{text}"

    @staticmethod
    def character_decision_prompt(situation: str, story_context: str) -> str:
        """Create character decision prompt."""
        return (
            f"Context: {story_context}\n\n"
            f"Situation: {situation}\n\n"
            f"What would you choose? Reply with only 'A', 'B', or 'C'."
        )

    @staticmethod
    def next_situation_prompt(
        story_so_far: str,
        characters: List[str],
        recent_decisions: List[Dict[str, str]]
    ) -> str:
        """Create next situation prediction prompt."""
        chars = ", ".join(characters)
        decisions_str = "\n".join([
            f"- {d.get('character', 'Unknown')} chose {d.get('choice', 'unknown')}"
            for d in recent_decisions
        ])

        return (
            f"Story: {story_so_far}\n\n"
            f"Characters: {chars}\n\n"
            f"Recent decisions:\n{decisions_str}\n\n"
            f"What happens next?"
        )

    @staticmethod
    def situation_choices_prompt(situation: str, character_name: str) -> str:
        """Create situation choices generation prompt."""
        return (
            f"Situation: {situation}\n\n"
            f"Character: {character_name}\n\n"
            f"Generate 3 choices in format:\n"
            f"A: [action]\n"
            f"B: [opposing action]\n"
            f"C: [abandon]"
        )

    @staticmethod
    def world_description_prompt(
        world_name: str,
        world_type: str,
        num_locations: int,
        num_entities: int
    ) -> str:
        """Create world description generation prompt."""
        return (
            f"Generate a vivid description for a {world_type} world named '{world_name}'. "
            f"The world has {num_locations} locations and {num_entities} inhabitants. "
            f"Create a 2-3 paragraph description that captures the essence, atmosphere, "
            f"and unique characteristics of this world. Make it engaging and immersive."
        )

    @staticmethod
    def story_description_prompt(
        story_title: str,
        genre: str,
        world_context: str,
        characters: List[str],
        locations: List[str]
    ) -> str:
        """Create story description generation prompt."""
        chars = ", ".join(characters) if characters else "various characters"
        locs = ", ".join(locations) if locations else "multiple locations"

        return (
            f"Generate an engaging description for a {genre} story titled '{story_title}'. "
            f"The story takes place in: {world_context}. "
            f"Main characters: {chars}. "
            f"Key locations: {locs}. "
            f"Create a 2-3 paragraph description that sets up the premise, introduces conflict, "
            f"and hooks the reader. Make it compelling and genre-appropriate."
        )

    @staticmethod
    def format_character_traits(traits: Dict[str, Any]) -> str:
        """Format character traits for prompts."""
        return ", ".join([f"{k}: {v}" for k, v in traits.items()])


class ResponseParsers:
    """Parsers for GPT responses."""

    @staticmethod
    def parse_decision(response_text: str) -> str:
        """
        Parse character decision from GPT response.

        Args:
            response_text: Raw GPT response

        Returns:
            Decision choice ('A', 'B', or 'C')
        """
        decision = response_text.strip().upper()

        # Check if it's a direct response
        if decision in ['A', 'B', 'C']:
            return decision

        # Try to extract from longer response
        # Look for standalone letters (not part of words)
        import re
        # Match A, B, or C as standalone characters
        match = re.search(r'\b([ABC])\b', decision)
        if match:
            return match.group(1)

        # Last resort: check if letter appears anywhere
        for char in ['A', 'B', 'C']:
            if char in decision:
                return char

        return 'A'  # Default

    @staticmethod
    def parse_choices(response_text: str) -> List[Dict[str, str]]:
        """
        Parse situation choices from GPT response.

        Args:
            response_text: Raw GPT response

        Returns:
            List of choice dictionaries [{'id': 'A', 'text': '...'}, ...]
        """
        lines = response_text.strip().split('\n')
        choices = []

        for line in lines:
            if line.startswith('A:'):
                choices.append({'id': 'A', 'text': line[2:].strip()})
            elif line.startswith('B:'):
                choices.append({'id': 'B', 'text': line[2:].strip()})
            elif line.startswith('C:'):
                choices.append({'id': 'C', 'text': line[2:].strip()})

        # Ensure we have exactly 3 choices
        if len(choices) < 3:
            default_choices = [
                {'id': 'A', 'text': 'Take action'},
                {'id': 'B', 'text': 'Take opposing action'},
                {'id': 'C', 'text': 'Abandon the situation'}
            ]
            return default_choices

        return choices[:3]

    @staticmethod
    def clean_description(response_text: str) -> str:
        """
        Clean and format description text.

        Args:
            response_text: Raw GPT response

        Returns:
            Cleaned description text
        """
        # Remove extra whitespace and normalize line breaks
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        return '\n\n'.join(lines)


# Convenience functions for backward compatibility
def get_translation_messages(text: str) -> List[Dict[str, str]]:
    """Get messages for translation request."""
    return [
        {"role": "system", "content": PromptTemplates.TRANSLATOR_SYSTEM},
        {"role": "user", "content": PromptTemplates.translation_prompt(text)}
    ]


def get_character_decision_messages(
    character_name: str,
    situation: str,
    story_context: str,
    character_traits: Dict[str, Any]
) -> List[Dict[str, str]]:
    """Get messages for character decision request."""
    traits_str = PromptTemplates.format_character_traits(character_traits)
    system_prompt = PromptTemplates.CHARACTER_DECISION_SYSTEM.format(
        character_name=character_name,
        traits=traits_str
    )

    return [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": PromptTemplates.character_decision_prompt(situation, story_context)
        }
    ]


def get_next_situation_messages(
    story_so_far: str,
    character_states: List[Dict[str, Any]],
    recent_decisions: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    """Get messages for next situation prediction."""
    characters = [c.get('name', 'Unknown') for c in character_states]

    return [
        {"role": "system", "content": PromptTemplates.STORYTELLER_SYSTEM},
        {
            "role": "user",
            "content": PromptTemplates.next_situation_prompt(
                story_so_far,
                characters,
                recent_decisions
            )
        }
    ]


def get_situation_choices_messages(
    situation: str,
    character_name: str
) -> List[Dict[str, str]]:
    """Get messages for situation choices generation."""
    return [
        {"role": "system", "content": PromptTemplates.CHOICE_GENERATOR_SYSTEM},
        {
            "role": "user",
            "content": PromptTemplates.situation_choices_prompt(situation, character_name)
        }
    ]


def get_world_description_messages(
    world_name: str,
    world_type: str,
    num_locations: int,
    num_entities: int
) -> List[Dict[str, str]]:
    """Get messages for world description generation."""
    return [
        {"role": "system", "content": PromptTemplates.WORLD_DESCRIPTION_SYSTEM},
        {
            "role": "user",
            "content": PromptTemplates.world_description_prompt(
                world_name, world_type, num_locations, num_entities
            )
        }
    ]


def get_story_description_messages(
    story_title: str,
    genre: str,
    world_context: str,
    characters: List[str],
    locations: List[str]
) -> List[Dict[str, str]]:
    """Get messages for story description generation."""
    return [
        {"role": "system", "content": PromptTemplates.STORY_DESCRIPTION_SYSTEM},
        {
            "role": "user",
            "content": PromptTemplates.story_description_prompt(
                story_title, genre, world_context, characters, locations
            )
        }
    ]
