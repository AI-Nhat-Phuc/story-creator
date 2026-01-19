"""Story generator using prompts and algorithms."""

from typing import Dict, Any, Optional, List
from core.models import Story, TimeCone

class StoryGenerator:
    """Generates stories based on prompts and world context."""

    def __init__(self):
        pass

    def _analyze_title_with_gpt(self, description: str, current_title: str) -> str:
        """
        Use GPT to analyze the description and suggest a better title if possible.
        Returns the new title if suggested, otherwise returns the current title.
        """
        try:
            from services.gpt_service import GPTService
            from ai.gpt_client import GPTIntegration
            gpt = GPTIntegration()
            gpt_service = GPTService(gpt)
            # Synchronous GPT call for title extraction
            result = gpt_service.analyze_story_title_sync(
                description=description,
                current_title=current_title
            )
            if result and isinstance(result, dict):
                new_title = result.get('title')
                if new_title and isinstance(new_title, str) and new_title.strip():
                    return new_title.strip()
            return current_title
        except Exception:
            return current_title


    def generate(
        self,
        title: str,
        description: str,
        world_id: str,
        genre: str = "adventure",
        locations: Optional[List[str]] = None,
        entities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Story:
        """
        Generate a story based on a description.

        Args:
            description: Description of the desired story
            world_id: ID of the world this story belongs to
            genre: Story genre (adventure, mystery, conflict, discovery)
            locations: Optional list of location IDs
            entities: Optional list of entity IDs
            metadata: Additional metadata

        Returns:
            Generated Story object
        """
        # Fallback title if GPT fails
        fallback_title = title if title and isinstance(title, str) and title.strip() else "Untitled Story"
        new_title = self._analyze_title_with_gpt(description, current_title=fallback_title)
        if not new_title or not isinstance(new_title, str) or not new_title.strip():
            new_title = fallback_title

        # Add genre to metadata
        story_metadata = metadata or {}
        story_metadata["genre"] = genre
        story_metadata["description"] = description

        story = Story(
            title=new_title,
            content=description,
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
        reference_event: str = "Story beginning",
        time_index: int = 0
    ) -> TimeCone:
        """
        Generate a time cone for a story.

        Args:
            story: Story to create time cone for
            world_id: ID of the world
            reference_event: Reference event for the time cone
            time_index: Numerical index for timeline ordering (0-100)

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
            story_id=story.story_id,
            time_index=time_index,
            metadata={"story_id": story.story_id}
        )

        story.add_time_cone(time_cone.time_cone_id)

        return time_cone


