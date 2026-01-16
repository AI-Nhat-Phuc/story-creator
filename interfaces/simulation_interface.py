"""Interactive simulation interface for character story mode."""

import sys
from typing import Optional, List, Dict, Any
from models import World, Story, Entity
from utils import NoSQLStorage, Storage
from utils.gpt_integration import GPTIntegration
from utils.simulation import SimulationState, CharacterTimeline


class SimulationInterface:
    """Interactive interface for character simulation mode."""
    
    def __init__(self, storage, gpt: Optional[GPTIntegration] = None):
        """
        Initialize simulation interface.
        
        Args:
            storage: Storage backend (NoSQL or JSON)
            gpt: GPT integration instance (optional, for AI features)
        """
        self.storage = storage
        self.gpt = gpt
        self.simulation: Optional[SimulationState] = None
        self.auto_translate = False
    
    def start_simulation(self, world_id: str) -> None:
        """
        Start a new simulation for a world.
        
        Args:
            world_id: World ID to simulate
        """
        print("\n" + "="*70)
        print("  CHARACTER SIMULATION MODE")
        print("="*70)
        
        # Load world
        world_data = self.storage.load_world(world_id)
        if not world_data:
            print(f"❌ World {world_id} not found")
            return
        
        world = World.from_dict(world_data)
        print(f"\n📖 World: {world.name}")
        print(f"   {world.description}")
        
        # Load stories
        stories = self.storage.list_stories(world_id)
        if not stories:
            print("\n❌ No stories found in this world")
            return
        
        print(f"\n✅ Found {len(stories)} stories")
        
        # Initialize simulation
        story_ids = [s['story_id'] for s in stories]
        self.simulation = SimulationState(world_id, story_ids)
        
        # Collect all entities from stories
        entity_ids = set()
        for story in stories:
            entity_ids.update(story.get('entities', []))
        
        print(f"\n👥 Characters in simulation: {len(entity_ids)}")
        
        # Load entities and let user choose which to control
        for entity_id in entity_ids:
            entity_data = self.storage.load_entity(entity_id)
            if entity_data:
                self.simulation.add_character(
                    entity_id,
                    entity_data['name'],
                    player_controlled=False  # Will be set later
                )
        
        # Check for GPT features
        if self.gpt:
            print("\n🤖 GPT-4 features enabled")
            enable_translation = input("   Enable auto-translation (ENG→VN)? (y/n): ").strip().lower()
            self.auto_translate = enable_translation == 'y'
        
        # Let user choose character to control
        self.choose_player_character()
        
        # Start simulation loop
        self.simulation_loop()
    
    def choose_player_character(self) -> None:
        """Let user choose which character to control."""
        print("\n" + "-"*70)
        print("Choose your character:")
        print("-"*70)
        
        characters = list(self.simulation.timelines.values())
        for i, timeline in enumerate(characters, 1):
            print(f"{i}. {timeline.entity_name}")
        
        print(f"{len(characters) + 1}. Watch all characters (AI-controlled)")
        
        while True:
            try:
                choice = int(input("\nEnter number: ").strip())
                if 1 <= choice <= len(characters):
                    selected = characters[choice - 1]
                    selected.is_player_controlled = True
                    print(f"\n✅ You are now: {selected.entity_name}")
                    break
                elif choice == len(characters) + 1:
                    print("\n👁️ Watching as observer")
                    break
                else:
                    print("Invalid choice")
            except ValueError:
                print("Please enter a number")
    
    def simulation_loop(self) -> None:
        """Main simulation loop."""
        print("\n" + "="*70)
        print("  SIMULATION STARTED")
        print("="*70)
        
        # Simulate 5 time steps
        for time_step in range(5):
            print(f"\n⏰ Time Index: {self.simulation.global_time_index}")
            print("-"*70)
            
            # Process each character
            for entity_id, timeline in self.simulation.timelines.items():
                entity_data = self.storage.load_entity(entity_id)
                if not entity_data:
                    continue
                
                # Generate situation
                situation = f"Time {self.simulation.global_time_index}: {entity_data['name']} faces a new challenge."
                
                if self.auto_translate and self.gpt:
                    # Translate situation
                    if situation not in self.simulation.translations:
                        translation = self.gpt.translate_eng_to_vn(situation)
                        self.simulation.add_translation(situation, translation)
                
                # Create event
                event = self.simulation.create_situation(
                    entity_id,
                    situation,
                    f"Character: {entity_data['name']}"
                )
                
                # Generate choices
                if self.gpt:
                    choices = self.gpt.generate_situation_choices(situation, entity_data['name'])
                else:
                    choices = [
                        {'id': 'A', 'text': 'Take action'},
                        {'id': 'B', 'text': 'Take opposing action'},
                        {'id': 'C', 'text': 'Abandon the situation'}
                    ]
                
                event['choices'] = choices
                
                # Make decision
                if timeline.is_player_controlled:
                    # Player choice
                    print(f"\n🎮 {entity_data['name']}'s turn:")
                    print(f"   Situation: {situation}")
                    
                    if self.auto_translate:
                        translated = self.simulation.get_translation(situation)
                        print(f"   (Tiếng Việt: {translated})")
                    
                    print("\n   Choices:")
                    for choice in choices:
                        print(f"   {choice['id']}. {choice['text']}")
                    
                    while True:
                        decision = input("\n   Your choice (A/B/C): ").strip().upper()
                        if decision in ['A', 'B', 'C']:
                            break
                        print("   Invalid choice. Please enter A, B, or C")
                    
                    chosen = next((c for c in choices if c['id'] == decision), choices[0])
                    print(f"   ✅ You chose: {chosen['text']}")
                else:
                    # AI choice
                    if self.gpt:
                        decision = self.gpt.generate_character_decision(
                            entity_data['name'],
                            situation,
                            f"Character traits: {entity_data.get('attributes', {})}",
                            entity_data.get('attributes', {})
                        )
                    else:
                        decision = 'A'  # Default
                    
                    chosen = next((c for c in choices if c['id'] == decision), choices[0])
                    print(f"\n🤖 {entity_data['name']} chose: {decision} - {chosen['text']}")
                
                event['decision'] = decision
                event['choice_text'] = chosen['text']
                timeline.add_event(event)
                
                self.simulation.record_decision(
                    entity_id,
                    event['event_id'],
                    decision,
                    chosen['text']
                )
            
            self.simulation.advance_global_time()
            
            # Predict next situation if GPT enabled
            if self.gpt and time_step < 4:
                print("\n🔮 Predicting next situation...")
                character_states = [
                    {'name': t.entity_name}
                    for t in self.simulation.timelines.values()
                ]
                recent = self.simulation.simulation_history[-len(self.simulation.timelines):]
                prediction = self.gpt.predict_next_situation(
                    f"Time {self.simulation.global_time_index} simulation",
                    character_states,
                    recent
                )
                print(f"   {prediction}")
        
        # Show final stories
        self.show_character_stories()
    
    def show_character_stories(self) -> None:
        """Show the complete story for each character."""
        print("\n" + "="*70)
        print("  SIMULATION COMPLETE - CHARACTER STORIES")
        print("="*70)
        
        for entity_id, timeline in self.simulation.timelines.items():
            story = self.simulation.get_character_story(entity_id, self.auto_translate)
            print(f"\n{story}")
            print("-"*70)
        
        # Show simulation stats
        print("\n📊 Simulation Statistics:")
        stats = self.simulation.to_dict()
        print(f"   - Global time index: {stats['global_time_index']}")
        print(f"   - Characters: {stats['character_count']}")
        print(f"   - Decisions made: {stats['history_count']}")
        print(f"   - Translations: {stats['translations_count']}")


def main():
    """Main entry point for simulation mode."""
    print("Story Creator - Simulation Mode")
    print("="*70)
    
    # Check for API key
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Initialize storage
    storage = NoSQLStorage("story_creator.db")
    
    # Initialize GPT if API key available
    gpt = None
    if api_key:
        try:
            gpt = GPTIntegration(api_key)
            print("✅ GPT-4 integration enabled")
        except Exception as e:
            print(f"⚠️ GPT-4 not available: {e}")
            print("   Simulation will run without AI features")
    else:
        print("⚠️ OPENAI_API_KEY not set. GPT features disabled.")
    
    # List available worlds
    worlds = storage.list_worlds()
    if not worlds:
        print("\n❌ No worlds found. Create a world first.")
        return
    
    print(f"\n📚 Available worlds:")
    for i, world in enumerate(worlds, 1):
        print(f"{i}. {world['name']}")
    
    # Choose world
    while True:
        try:
            choice = int(input("\nSelect world number: ").strip())
            if 1 <= choice <= len(worlds):
                selected_world = worlds[choice - 1]
                break
            print("Invalid choice")
        except ValueError:
            print("Please enter a number")
    
    # Start simulation
    interface = SimulationInterface(storage, gpt)
    interface.start_simulation(selected_world['world_id'])
    
    storage.close()


if __name__ == "__main__":
    main()
