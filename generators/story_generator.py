"""Story generator using prompts and algorithms."""

import random
from typing import Dict, Any, Optional, List
from models.story import Story
from models.time_cone import TimeCone


class StoryGenerator:
    """Generates stories based on prompts and world context."""
    
    # Story templates by genre
    STORY_TEMPLATES = {
        "adventure": [
            "A journey to {location} where {entity} discovers {element}",
            "{entity} embarks on a quest to find {element} in {location}",
            "An unexpected adventure leads {entity} to {location}"
        ],
        "mystery": [
            "A strange occurrence in {location} draws {entity} into investigation",
            "{entity} uncovers secrets about {element} in {location}",
            "The mystery of {location} challenges {entity}"
        ],
        "conflict": [
            "{entity} faces a great challenge in {location}",
            "A battle for {element} unfolds in {location}",
            "{entity} must defend {location} against threats"
        ],
        "discovery": [
            "{entity} makes a groundbreaking discovery in {location}",
            "Hidden knowledge about {element} is revealed to {entity}",
            "An ancient secret in {location} changes everything for {entity}"
        ]
    }
    
    def __init__(self):
        """Initialize the StoryGenerator."""
        pass
    
    def generate(
        self,
        prompt: str,
        world_id: str,
        genre: str = "adventure",
        locations: Optional[List[str]] = None,
        entities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Story:
        """
        Generate a story based on a prompt.
        
        Args:
            prompt: User prompt describing the desired story
            world_id: ID of the world this story belongs to
            genre: Story genre (adventure, mystery, conflict, discovery)
            locations: Optional list of location IDs
            entities: Optional list of entity IDs
            metadata: Additional metadata
            
        Returns:
            Generated Story object
        """
        # Extract title from prompt or generate one
        title = self._extract_title(prompt) or self._generate_title(genre)
        
        # Generate story content
        content = self._generate_content(prompt, genre)
        
        # Add genre to metadata
        story_metadata = metadata or {}
        story_metadata["genre"] = genre
        story_metadata["prompt"] = prompt
        
        story = Story(
            title=title,
            content=content,
            world_id=world_id,
            metadata=story_metadata
        )
        
        # Add locations if provided
        if locations:
            for location_id in locations:
                story.add_location(location_id)
        
        # Add entities if provided
        if entities:
            for entity_id in entities:
                story.add_entity(entity_id)
        
        return story
    
    def generate_time_cone(
        self,
        story: Story,
        world_id: str,
        reference_event: str = "Story beginning"
    ) -> TimeCone:
        """
        Generate a time cone for a story.
        
        Args:
            story: Story to create time cone for
            world_id: ID of the world
            reference_event: Reference event for the time cone
            
        Returns:
            Generated TimeCone object
        """
        name = f"Timeline: {story.title}"
        description = f"Temporal context for the story '{story.title}'"
        
        # Create time markers
        start_time = "Beginning"
        end_time = "End"
        
        time_cone = TimeCone(
            name=name,
            description=description,
            world_id=world_id,
            start_time=start_time,
            end_time=end_time,
            reference_event=reference_event,
            metadata={"story_id": story.story_id}
        )
        
        story.add_time_cone(time_cone.time_cone_id)
        
        return time_cone
    
    def _extract_title(self, prompt: str) -> Optional[str]:
        """Extract story title from prompt."""
        # Look for title indicators
        keywords = ["titled ", "called ", "story of ", "tale of "]
        prompt_lower = prompt.lower()
        
        for keyword in keywords:
            if keyword in prompt_lower:
                idx = prompt_lower.index(keyword) + len(keyword)
                # Get the next few words
                remaining = prompt[idx:].split()
                if remaining:
                    return " ".join(remaining[:5]).strip('.,!?\'"')
        
        return None
    
    def _generate_title(self, genre: str) -> str:
        """Generate a title based on genre."""
        title_parts = {
            "adventure": ["The Quest", "Journey", "Adventure", "Voyage", "Expedition"],
            "mystery": ["The Mystery", "Secret", "Enigma", "Case", "Investigation"],
            "conflict": ["The Battle", "War", "Conflict", "Struggle", "Confrontation"],
            "discovery": ["The Discovery", "Revelation", "Finding", "Uncovering", "Awakening"]
        }
        
        parts = title_parts.get(genre, ["The Story"])
        base_title = random.choice(parts)
        
        # Add a descriptor
        descriptors = ["Begins", "Unfolds", "Continues", "of Destiny", "of Fate"]
        descriptor = random.choice(descriptors)
        
        return f"{base_title} {descriptor}"
    
    def _generate_content(self, prompt: str, genre: str) -> str:
        """Generate story content based on prompt and genre."""
        # Start with the prompt as base content
        content = prompt
        
        # Add genre-specific elements
        if genre in self.STORY_TEMPLATES:
            templates = self.STORY_TEMPLATES[genre]
            template = random.choice(templates)
            
            # Simple template filling
            filled_template = template.replace("{location}", "a mysterious place")
            filled_template = filled_template.replace("{entity}", "the protagonist")
            filled_template = filled_template.replace("{element}", "something important")
            
            content += f"\n\n{filled_template}"
        
        # Add conclusion
        content += "\n\nThe story unfolds with unexpected turns and meaningful moments."
        
        return content
