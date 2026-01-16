#!/usr/bin/env python
"""Demo script showcasing NoSQL database performance."""

from models import World, Story, Location, Entity, TimeCone
from generators import WorldGenerator, StoryGenerator, StoryLinker
from utils import NoSQLStorage
import json
import time


def print_section(title):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def main():
    """Run the NoSQL demo."""
    print_section("STORY CREATOR - NoSQL DATABASE DEMO")
    
    # Initialize NoSQL storage
    storage = NoSQLStorage("demo_nosql.db")
    storage.clear_all()  # Start fresh
    
    world_gen = WorldGenerator()
    story_gen = StoryGenerator()
    story_linker = StoryLinker()
    
    print("✅ NoSQL database initialized: demo_nosql.db")
    print(f"   Initial stats: {storage.get_stats()}")
    
    # 1. Performance test - Create multiple worlds
    print_section("1. Performance Test - Creating Worlds")
    
    start_time = time.time()
    
    worlds = []
    for i in range(5):
        world = world_gen.generate(
            prompt=f"Thế giới thứ {i+1} với các đặc điểm độc đáo",
            world_type=["fantasy", "sci-fi", "modern", "historical"][i % 4]
        )
        
        # Generate locations and entities
        locations = world_gen.generate_locations(world, count=3)
        entities = world_gen.generate_entities(world, count=3)
        
        # Save to database
        storage.save_world(world.to_dict())
        for loc in locations:
            storage.save_location(loc.to_dict())
        for ent in entities:
            storage.save_entity(ent.to_dict())
        
        worlds.append(world)
        print(f"Created world {i+1}: {world.name}")
    
    creation_time = time.time() - start_time
    print(f"\n⏱️  Created 5 worlds with locations and entities in {creation_time:.3f}s")
    print(f"   Database stats: {storage.get_stats()}")
    
    # 2. Performance test - Create stories
    print_section("2. Performance Test - Creating Stories")
    
    start_time = time.time()
    
    all_stories = []
    for world in worlds[:3]:  # Create stories for first 3 worlds
        for j in range(3):  # 3 stories per world
            story = story_gen.generate(
                prompt=f"Câu chuyện {j+1} trong thế giới {world.name}",
                world_id=world.world_id,
                genre=["adventure", "mystery", "conflict"][j],
                locations=world.locations[:2],
                entities=world.entities[:2]
            )
            
            time_cone = story_gen.generate_time_cone(story, world.world_id)
            
            storage.save_story(story.to_dict())
            storage.save_time_cone(time_cone.to_dict())
            
            world.add_story(story.story_id)
            storage.save_world(world.to_dict())
            
            all_stories.append(story)
    
    story_creation_time = time.time() - start_time
    print(f"⏱️  Created 9 stories in {story_creation_time:.3f}s")
    print(f"   Database stats: {storage.get_stats()}")
    
    # 3. Performance test - Query operations
    print_section("3. Performance Test - Query Operations")
    
    # Query all worlds
    start_time = time.time()
    queried_worlds = storage.list_worlds()
    query_time = time.time() - start_time
    print(f"⏱️  Queried {len(queried_worlds)} worlds in {query_time:.6f}s")
    
    # Query stories by world
    start_time = time.time()
    for world in worlds[:3]:
        stories = storage.list_stories(world.world_id)
        print(f"   World '{world.name}': {len(stories)} stories")
    query_time = time.time() - start_time
    print(f"⏱️  Filtered queries completed in {query_time:.6f}s")
    
    # 4. Link stories (same as before)
    print_section("4. Story Linking")
    
    story_linker.link_stories(
        all_stories,
        link_by_entities=True,
        link_by_locations=True,
        link_by_time=True
    )
    
    # Update in database
    for story in all_stories:
        storage.save_story(story.to_dict())
    
    linked_count = sum(1 for s in all_stories if s.linked_stories)
    print(f"✅ Linked {linked_count} out of {len(all_stories)} stories")
    
    # 5. Database operations
    print_section("5. Database Operations")
    
    # Update operation
    test_world = worlds[0]
    test_world.metadata["updated"] = True
    storage.save_world(test_world.to_dict())
    
    loaded_world = storage.load_world(test_world.world_id)
    print(f"✅ Update test: {'updated' in loaded_world.get('metadata', {})}")
    
    # Load operation
    start_time = time.time()
    for world in worlds:
        loaded = storage.load_world(world.world_id)
    load_time = time.time() - start_time
    print(f"⏱️  Loaded {len(worlds)} worlds in {load_time:.6f}s")
    
    # 6. Final statistics
    print_section("6. Final Database Statistics")
    
    stats = storage.get_stats()
    print(f"Total entries in database:")
    print(f"  - Worlds:     {stats['worlds']}")
    print(f"  - Stories:    {stats['stories']}")
    print(f"  - Locations:  {stats['locations']}")
    print(f"  - Entities:   {stats['entities']}")
    print(f"  - Time Cones: {stats['time_cones']}")
    print(f"  - TOTAL:      {sum(stats.values())}")
    
    # 7. Show data examples
    print_section("7. NoSQL Data Examples")
    
    print("Sample World from database:")
    print(json.dumps(queried_worlds[0], indent=2, ensure_ascii=False)[:300] + "...")
    
    print("\n\nSample Story from database:")
    sample_story = storage.list_stories()[0]
    print(json.dumps(sample_story, indent=2, ensure_ascii=False)[:300] + "...")
    
    # 8. Comparison note
    print_section("8. NoSQL vs JSON Comparison")
    
    print("✅ Advantages of NoSQL Database:")
    print("  - Faster query performance with indexing")
    print("  - Efficient filtering and searching")
    print("  - Single file database (easier backup)")
    print("  - ACID transactions support")
    print("  - Better for large datasets")
    print("  - Concurrent access support")
    
    print("\n📊 Performance Results:")
    print(f"  - World creation: {creation_time:.3f}s for 5 worlds")
    print(f"  - Story creation: {story_creation_time:.3f}s for 9 stories")
    print(f"  - Query speed: {query_time:.6f}s for filtered queries")
    print(f"  - Load speed: {load_time:.6f}s for {len(worlds)} worlds")
    
    print_section("DEMO COMPLETE")
    print(f"✅ Database file: demo_nosql.db")
    print(f"   Total entries: {sum(stats.values())}")
    print("\n💡 Try the NoSQL interface:")
    print("   python main.py -i terminal -s nosql")
    print("   python main.py -i gui -s nosql")
    
    # Close database
    storage.close()


if __name__ == "__main__":
    main()
