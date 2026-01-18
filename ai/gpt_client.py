"""GPT-5 Nano integration for story creator system."""

import os
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Import prompt templates
from .prompts import (
    PromptTemplates,
    ResponseParsers,
    get_translation_messages,
    get_character_decision_messages,
    get_next_situation_messages,
    get_situation_choices_messages,
    get_world_description_messages,
    get_story_description_messages
)


class GPTIntegration:
    """Handles GPT-5 Mini integration for translation and character simulation."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GPT integration.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        if OpenAI is None:
            raise ImportError("openai package not installed. Install with: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter.")

        self.client = OpenAI(api_key=self.api_key)
        # Using GPT-4o-mini - Latest compact model
        self.model = "gpt-4o-mini"
        logger.info(f"GPT client initialized with model: {self.model}")

    def translate_eng_to_vn(self, text: str) -> str:
        """
        Translate English text to Vietnamese.

        Args:
            text: English text to translate

        Returns:
            Vietnamese translation
        """
        try:
            logger.debug(f"Translating text: {text[:50]}...")
            messages = get_translation_messages(text)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            result = response.choices[0].message.content.strip()
            logger.info(f"Translation complete: {len(result)} characters")
            return result
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return f"Translation error: {str(e)}"

    def generate_character_decision(
        self,
        character_name: str,
        situation: str,
        story_context: str,
        character_traits: Dict[str, Any]
    ) -> str:
        """
        Generate a decision for a non-player character using GPT.

        Args:
            character_name: Name of the character
            situation: Current situation description
            story_context: Context from the story
            character_traits: Character attributes and traits

        Returns:
            The decision choice (A, B, or C)
        """
        try:
            logger.debug(f"Generating decision for {character_name}")
            messages = get_character_decision_messages(
                character_name, situation, story_context, character_traits
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=10
            )

            decision_text = response.choices[0].message.content
            decision = ResponseParsers.parse_decision(decision_text)
            logger.info(f"{character_name} chose: {decision}")
            return decision
        except Exception as e:
            logger.error(f"Error generating decision for {character_name}: {e}")
            return 'A'  # Default choice on error

    def predict_next_situation(
        self,
        story_so_far: str,
        character_states: List[Dict[str, Any]],
        recent_decisions: List[Dict[str, Any]]
    ) -> str:
        """
        Predict the next situation based on story and character decisions.

        Args:
            story_so_far: Story narrative up to this point
            character_states: Current state of all characters
            recent_decisions: Recent decisions made by characters

        Returns:
            Predicted next situation
        """
        try:
            messages = get_next_situation_messages(
                story_so_far, character_states, recent_decisions
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=150
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to predict: {str(e)}"

    def generate_situation_choices(
        self,
        situation: str,
        character_name: str
    ) -> List[Dict[str, str]]:
        """
        Generate 3 choices for a situation (2 opposing + 1 abandon).

        Args:
            situation: Current situation description
            character_name: Name of the character making the choice

        Returns:
            List of 3 choice dictionaries
        """
        try:
            messages = get_situation_choices_messages(situation, character_name)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=200
            )

            content = response.choices[0].message.content
            return ResponseParsers.parse_choices(content)
        except Exception as e:
            print(f"Error generating choices: {e}")
            return [
                {'id': 'A', 'text': 'Take action'},
                {'id': 'B', 'text': 'Take opposing action'},
                {'id': 'C', 'text': 'Abandon the situation'}
            ]
