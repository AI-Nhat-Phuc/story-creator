"""Character simulation system with timeline management."""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from models import Entity, Story, TimeCone


class CharacterTimeline:
    """Represents a character's timeline in the story."""
    
    def __init__(self, entity_id: str, entity_name: str):
        """
        Initialize character timeline.
        
        Args:
            entity_id: Entity ID
            entity_name: Character name
        """
        self.entity_id = entity_id
        self.entity_name = entity_name
        self.events: List[Dict[str, Any]] = []
        self.current_time_index = 0
        self.is_player_controlled = False
    
    def add_event(self, event: Dict[str, Any]) -> None:
        """
        Add an event to the timeline.
        
        Args:
            event: Event dictionary with time_index, situation, choices, decision
        """
        self.events.append(event)
        self.events.sort(key=lambda x: x.get('time_index', 0))
    
    def get_chronological_story(self) -> List[Dict[str, Any]]:
        """
        Get events in chronological order by light cone time.
        
        Returns:
            List of events sorted by time
        """
        return sorted(self.events, key=lambda x: x.get('time_index', 0))
    
    def get_current_event(self) -> Optional[Dict[str, Any]]:
        """Get the current event at the timeline position."""
        if self.current_time_index < len(self.events):
            return self.events[self.current_time_index]
        return None
    
    def advance_timeline(self) -> bool:
        """
        Advance to next event in timeline.
        
        Returns:
            True if advanced, False if at end
        """
        if self.current_time_index < len(self.events) - 1:
            self.current_time_index += 1
            return True
        return False


class SimulationState:
    """Manages the state of the story simulation."""
    
    def __init__(self, world_id: str, story_ids: List[str]):
        """
        Initialize simulation state.
        
        Args:
            world_id: World ID
            story_ids: List of story IDs to simulate
        """
        self.simulation_id = str(uuid.uuid4())
        self.world_id = world_id
        self.story_ids = story_ids
        self.timelines: Dict[str, CharacterTimeline] = {}
        self.global_time_index = 0
        self.translations: Dict[str, str] = {}  # Original text -> Vietnamese
        self.simulation_history: List[Dict[str, Any]] = []
    
    def add_character(self, entity_id: str, entity_name: str, player_controlled: bool = False) -> None:
        """
        Add a character to the simulation.
        
        Args:
            entity_id: Entity ID
            entity_name: Character name
            player_controlled: Whether this character is controlled by player
        """
        timeline = CharacterTimeline(entity_id, entity_name)
        timeline.is_player_controlled = player_controlled
        self.timelines[entity_id] = timeline
    
    def add_translation(self, original: str, translated: str) -> None:
        """
        Store a translation.
        
        Args:
            original: Original English text
            translated: Vietnamese translation
        """
        self.translations[original] = translated
    
    def get_translation(self, text: str) -> str:
        """
        Get translation or return original text.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text or original
        """
        return self.translations.get(text, text)
    
    def create_situation(
        self,
        entity_id: str,
        situation_text: str,
        story_context: str
    ) -> Dict[str, Any]:
        """
        Create a new situation event.
        
        Args:
            entity_id: Entity ID for the character
            situation_text: Situation description
            story_context: Story context
            
        Returns:
            Situation event dictionary
        """
        return {
            'event_id': str(uuid.uuid4()),
            'entity_id': entity_id,
            'time_index': self.global_time_index,
            'situation': situation_text,
            'context': story_context,
            'choices': [],
            'decision': None,
            'timestamp': datetime.now().isoformat()
        }
    
    def record_decision(
        self,
        entity_id: str,
        event_id: str,
        decision: str,
        choice_text: str
    ) -> None:
        """
        Record a character's decision.
        
        Args:
            entity_id: Entity ID
            event_id: Event ID
            decision: Decision ID (A, B, or C)
            choice_text: Text of the chosen option
        """
        self.simulation_history.append({
            'entity_id': entity_id,
            'event_id': event_id,
            'time_index': self.global_time_index,
            'decision': decision,
            'choice_text': choice_text,
            'timestamp': datetime.now().isoformat()
        })
    
    def advance_global_time(self) -> None:
        """Advance the global timeline."""
        self.global_time_index += 1
    
    def get_character_story(self, entity_id: str, include_translation: bool = True) -> str:
        """
        Get a character's story in chronological order.
        
        Args:
            entity_id: Entity ID
            include_translation: Whether to include Vietnamese translation
            
        Returns:
            Formatted story text
        """
        if entity_id not in self.timelines:
            return "Character not found in simulation."
        
        timeline = self.timelines[entity_id]
        events = timeline.get_chronological_story()
        
        story_parts = [f"=== Story of {timeline.entity_name} ===\n"]
        
        for event in events:
            situation = event.get('situation', '')
            decision = event.get('decision', 'N/A')
            choice_text = event.get('choice_text', '')
            
            part = f"\n[Time {event.get('time_index', 0)}]\n"
            part += f"Situation: {situation}\n"
            
            if include_translation and situation in self.translations:
                part += f"(Vietnamese: {self.translations[situation]})\n"
            
            if decision:
                part += f"Decision: {decision} - {choice_text}\n"
            
            story_parts.append(part)
        
        return "".join(story_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert simulation state to dictionary."""
        return {
            'simulation_id': self.simulation_id,
            'world_id': self.world_id,
            'story_ids': self.story_ids,
            'global_time_index': self.global_time_index,
            'character_count': len(self.timelines),
            'translations_count': len(self.translations),
            'history_count': len(self.simulation_history)
        }
