"""GPT-4o integration for story creator system."""

import os
from typing import Dict, Any, List, Optional
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class GPTIntegration:
    """Handles GPT-4o integration for translation and character simulation."""
    
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
        # Using GPT-4o - Latest multimodal model with improved performance and lower cost
        # Upgraded from gpt-4-turbo-preview for better quality and faster responses
        self.model = "gpt-4o"
    
    def translate_eng_to_vn(self, text: str) -> str:
        """
        Translate English text to Vietnamese.
        
        Args:
            text: English text to translate
            
        Returns:
            Vietnamese translation
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional English to Vietnamese translator. Translate the given text accurately while preserving the tone and style."
                    },
                    {
                        "role": "user",
                        "content": f"Translate this to Vietnamese:\n\n{text}"
                    }
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
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
        traits_str = ", ".join([f"{k}: {v}" for k, v in character_traits.items()])
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are {character_name}, a character with these traits: {traits_str}. Make decisions based on your character."
                    },
                    {
                        "role": "user",
                        "content": f"Context: {story_context}\n\nSituation: {situation}\n\nWhat would you choose? Reply with only 'A', 'B', or 'C'."
                    }
                ],
                temperature=0.7,
                max_tokens=10
            )
            
            decision = response.choices[0].message.content.strip().upper()
            if decision not in ['A', 'B', 'C']:
                return 'A'  # Default to A if invalid response
            return decision
        except Exception as e:
            print(f"Error generating decision: {e}")
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
        chars = ", ".join([c.get('name', 'Unknown') for c in character_states])
        decisions_str = "\n".join([
            f"- {d.get('character', 'Unknown')} chose {d.get('choice', 'unknown')}"
            for d in recent_decisions
        ])
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative storyteller. Based on the story and character decisions, predict what happens next in 2-3 sentences."
                    },
                    {
                        "role": "user",
                        "content": f"Story: {story_so_far}\n\nCharacters: {chars}\n\nRecent decisions:\n{decisions_str}\n\nWhat happens next?"
                    }
                ],
                temperature=0.8,
                max_tokens=150
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Generate exactly 3 choices for a story situation: Choice A (action), Choice B (opposing action), Choice C (abandon/retreat). Keep each choice to one sentence."
                    },
                    {
                        "role": "user",
                        "content": f"Situation: {situation}\n\nCharacter: {character_name}\n\nGenerate 3 choices in format:\nA: [action]\nB: [opposing action]\nC: [abandon]"
                    }
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            lines = content.split('\n')
            
            choices = []
            for line in lines:
                if line.startswith('A:'):
                    choices.append({'id': 'A', 'text': line[2:].strip()})
                elif line.startswith('B:'):
                    choices.append({'id': 'B', 'text': line[2:].strip()})
                elif line.startswith('C:'):
                    choices.append({'id': 'C', 'text': line[2:].strip()})
            
            # Ensure we have 3 choices
            if len(choices) < 3:
                choices = [
                    {'id': 'A', 'text': 'Take action'},
                    {'id': 'B', 'text': 'Take opposing action'},
                    {'id': 'C', 'text': 'Abandon the situation'}
                ]
            
            return choices[:3]
        except Exception as e:
            print(f"Error generating choices: {e}")
            return [
                {'id': 'A', 'text': 'Take action'},
                {'id': 'B', 'text': 'Take opposing action'},
                {'id': 'C', 'text': 'Abandon the situation'}
            ]
