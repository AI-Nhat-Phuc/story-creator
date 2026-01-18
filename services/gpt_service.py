"""GPT service for generating world and story descriptions."""

from typing import Optional, List, Dict
from ai.gpt_client import GPTIntegration
from ai.prompts import PromptTemplates


class GPTService:
    """Service for handling GPT-based content generation."""

    def __init__(self, gpt_integration: Optional[GPTIntegration] = None):
        """
        Initialize GPT service.

        Args:
            gpt_integration: GPTIntegration instance (optional)
        """
        self.gpt = gpt_integration

    def is_available(self) -> bool:
        """Check if GPT is available."""
        return self.gpt is not None

    def generate_world_description(
        self,
        world_type: str,
        callback_success,
        callback_error
    ) -> None:
        """
        Generate world description using GPT.

        Args:
            world_type: Type of world (fantasy, sci-fi, modern, historical)
            callback_success: Function to call with description on success
            callback_error: Function to call with error on failure
        """
        import threading

        def gpt_request():
            try:
                prompt = PromptTemplates.WORLD_DESCRIPTION_TEMPLATE.format(
                    world_type=world_type
                )

                response = self.gpt.client.chat.completions.create(
                    model=self.gpt.model,
                    messages=[
                        {"role": "system", "content": PromptTemplates.WORLD_GENERATOR_SYSTEM},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=300
                )

                description = response.choices[0].message.content.strip()
                callback_success(description)

            except Exception as e:
                callback_error(e)

        thread = threading.Thread(target=gpt_request, daemon=True)
        thread.start()

    def generate_story_description(
        self,
        genre: str,
        world_type: str,
        world_description: str,
        base_description: str = "",
        callback_success=None,
        callback_error=None
    ) -> None:
        """
        Generate story description using GPT.

        Args:
            genre: Story genre (adventure, mystery, conflict, discovery)
            world_type: Type of world
            world_description: Description of the world
            base_description: User's initial input to use as foundation (optional)
            callback_success: Function to call with description on success
            callback_error: Function to call with error on failure
        """
        import threading

        def gpt_request():
            try:
                if base_description:
                    prompt = PromptTemplates.STORY_DESCRIPTION_WITH_BASE_TEMPLATE.format(
                        base_description=base_description,
                        genre=genre,
                        world_type=world_type,
                        world_description=world_description[:200]
                    )
                else:
                    prompt = PromptTemplates.STORY_DESCRIPTION_NEW_TEMPLATE.format(
                        genre=genre,
                        world_type=world_type,
                        world_description=world_description[:200]
                    )

                response = self.gpt.client.chat.completions.create(
                    model=self.gpt.model,
                    messages=[
                        {"role": "system", "content": PromptTemplates.STORY_GENERATOR_SYSTEM},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=250
                )

                description = response.choices[0].message.content.strip()
                callback_success(description)

            except Exception as e:
                callback_error(e)

        thread = threading.Thread(target=gpt_request, daemon=True)
        thread.start()

    def analyze_world_entities(
        self,
        world_description: str,
        world_type: str,
        callback_success,
        callback_error
    ) -> None:
        """
        Analyze world description and extract entities and locations using GPT.

        Args:
            world_description: Description of the world
            world_type: Type of world (fantasy, sci-fi, modern, historical)
            callback_success: Function to call with analysis result on success
            callback_error: Function to call with error on failure
        """
        import threading
        import json

        def gpt_request():
            try:
                prompt = PromptTemplates.ANALYZE_WORLD_ENTITIES_TEMPLATE.format(
                    world_description=world_description,
                    world_type=world_type
                )

                response = self.gpt.client.chat.completions.create(
                    model=self.gpt.model,
                    messages=[
                        {"role": "system", "content": PromptTemplates.TEXT_ANALYZER_SYSTEM},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=1000,
                    response_format={"type": "json_object"}
                )

                result_text = response.choices[0].message.content.strip()
                result = json.loads(result_text)
                callback_success(result)

            except Exception as e:
                callback_error(e)

        thread = threading.Thread(target=gpt_request, daemon=True)
        thread.start()

    def analyze_story_entities(
        self,
        story_description: str,
        story_title: str = "",
        story_genre: str = "",
        callback_success=None,
        callback_error=None
    ) -> None:
        """
        Analyze story description and extract characters and locations using GPT.

        Args:
            story_description: Description of the story
            story_title: Title of the story (optional)
            story_genre: Genre of the story (optional)
            callback_success: Function to call with analysis result on success
            callback_error: Function to call with error on failure
        """
        import threading
        import json

        def gpt_request():
            try:
                prompt = PromptTemplates.ANALYZE_STORY_ENTITIES_TEMPLATE.format(
                    story_title=story_title if story_title else 'None',
                    story_genre=story_genre if story_genre else 'Unknown',
                    story_description=story_description
                )

                response = self.gpt.client.chat.completions.create(
                    model=self.gpt.model,
                    messages=[
                        {"role": "system", "content": PromptTemplates.TEXT_ANALYZER_SYSTEM},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=500,
                    response_format={"type": "json_object"}
                )

                result_text = response.choices[0].message.content.strip()
                result = json.loads(result_text)
                callback_success(result)

            except Exception as e:
                callback_error(e)

        thread = threading.Thread(target=gpt_request, daemon=True)
        thread.start()
