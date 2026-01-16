#!/usr/bin/env python
"""Demo script for GPT-4 integrated simulation mode."""

import os
from models import World, Story, Entity, Location, TimeCone
from generators import WorldGenerator, StoryGenerator
from utils import NoSQLStorage, GPTIntegration, SimulationState


def print_section(title):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def main():
    """Run the GPT integration demo."""
    print_section("STORY CREATOR - GPT-4 SIMULATION DEMO")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY not set.")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        print("\n   Running demo in limited mode (no GPT features)...")
        gpt = None
    else:
        print("✅ OpenAI API key found")
        try:
            gpt = GPTIntegration(api_key)
            print("✅ GPT-4 integration initialized")
        except Exception as e:
            print(f"❌ GPT-4 initialization failed: {e}")
            gpt = None
    
    # Initialize storage
    storage = NoSQLStorage("demo_simulation.db")
    storage.clear_all()
    
    print_section("1. Creating Demo World & Stories")
    
    # Generate world
    world_gen = WorldGenerator()
    world = world_gen.generate(
        prompt="A magical world where time travelers can alter history",
        world_type="fantasy"
    )
    
    # Generate entities
    entities = world_gen.generate_entities(world, count=3)
    
    # Save world and entities
    storage.save_world(world.to_dict())
    for entity in entities:
        storage.save_entity(entity.to_dict())
        world.add_entity(entity.entity_id)
    
    print(f"✅ Created world: {world.name}")
    print(f"   Characters:")
    for entity in entities:
        print(f"   - {entity.name} ({entity.entity_type})")
    
    # Generate stories
    story_gen = StoryGenerator()
    story1 = story_gen.generate(
        prompt="A warrior discovers a time portal",
        world_id=world.world_id,
        genre="adventure",
        entities=[entities[0].entity_id]
    )
    
    storage.save_story(story1.to_dict())
    world.add_story(story1.story_id)
    
    print(f"\n✅ Created story: {story1.title}")
    
    # Update world
    storage.save_world(world.to_dict())
    
    # Demonstrate GPT features
    if gpt:
        print_section("2. GPT-4 Translation Demo")
        
        sample_text = "The warrior faces a difficult choice at the crossroads."
        print(f"Original (EN): {sample_text}")
        
        translation = gpt.translate_eng_to_vn(sample_text)
        print(f"Translated (VN): {translation}")
        
        print_section("3. GPT-4 Choice Generation Demo")
        
        situation = "You discover an ancient artifact that could change history."
        choices = gpt.generate_situation_choices(situation, entities[0].name)
        
        print(f"Situation: {situation}")
        print(f"\nGenerated choices:")
        for choice in choices:
            print(f"  {choice['id']}. {choice['text']}")
        
        print_section("4. GPT-4 Decision Making Demo")
        
        decision = gpt.generate_character_decision(
            entities[1].name,
            situation,
            f"Story: {story1.content}",
            entities[1].attributes
        )
        
        print(f"Character: {entities[1].name}")
        print(f"Situation: {situation}")
        print(f"AI Decision: {decision}")
        
        print_section("5. GPT-4 Prediction Demo")
        
        character_states = [
            {'name': e.name, 'type': e.entity_type}
            for e in entities[:2]
        ]
        
        recent_decisions = [
            {'character': entities[0].name, 'choice': 'A - Take the artifact'},
            {'character': entities[1].name, 'choice': 'B - Reject the artifact'}
        ]
        
        prediction = gpt.predict_next_situation(
            story1.content,
            character_states,
            recent_decisions
        )
        
        print(f"Based on story and decisions:")
        print(f"Next situation prediction:\n{prediction}")
    
    # Demonstrate simulation
    print_section("6. Simulation State Demo")
    
    sim = SimulationState(world.world_id, [story1.story_id])
    
    # Add characters
    for entity in entities:
        sim.add_character(entity.entity_id, entity.name, player_controlled=False)
    
    # Make first character player-controlled
    list(sim.timelines.values())[0].is_player_controlled = True
    
    # Create sample events
    for i in range(3):
        for entity in entities:
            event = sim.create_situation(
                entity.entity_id,
                f"Time {i}: {entity.name} encounters a challenge",
                "Story context"
            )
            event['decision'] = 'A'
            event['choice_text'] = 'Take action'
            
            sim.timelines[entity.entity_id].add_event(event)
        
        sim.advance_global_time()
    
    print("Simulation created with:")
    print(f"  - {len(sim.timelines)} characters")
    print(f"  - {sim.global_time_index} time steps")
    
    # Show character story
    print("\nSample character timeline:")
    story_text = sim.get_character_story(entities[0].entity_id, include_translation=False)
    print(story_text[:400] + "...")
    
    # Show stats
    print("\nSimulation statistics:")
    stats = sim.to_dict()
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    print_section("7. Features Summary")
    
    print("✅ Implemented Features:")
    print("  1. Auto-translation (ENG→VN) with GPT-4")
    print("  2. Translation storage in database")
    print("  3. Character simulation mode")
    print("  4. Read character story chronologically by light cone time")
    print("  5. Interactive decision making (3 choices: 2 opposing + 1 abandon)")
    print("  6. AI-controlled characters (GPT makes decisions)")
    print("  7. Separate timeline for each character")
    print("  8. Shared global timeline")
    print("  9. Situation prediction based on story & decisions")
    
    print("\n💡 Usage:")
    print("   python main.py -i simulation")
    print("   (Set OPENAI_API_KEY for full GPT features)")
    
    print_section("DEMO COMPLETE")
    print(f"✅ Database: demo_simulation.db")
    print(f"   Characters: {len(entities)}")
    print(f"   Stories: 1")
    
    # Cleanup
    storage.close()


if __name__ == "__main__":
    main()
