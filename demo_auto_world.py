"""Demo script for auto-world generation feature."""

from generators.world_generator import WorldGenerator
from generators.story_generator import StoryGenerator
from utils.nosql_storage import NoSQLStorage


def demo_auto_generation():
    """Demonstrate the auto-generation feature."""
    print("="*70)
    print("DEMO: Tự động tạo thế giới khi chọn thể loại câu chuyện")
    print("="*70)
    
    generator = WorldGenerator()
    story_gen = StoryGenerator()
    storage = NoSQLStorage("demo_auto.db")
    
    # Test each genre
    genres = ["adventure", "mystery", "conflict", "discovery"]
    
    for genre in genres:
        print(f"\n{'='*70}")
        print(f"Thể loại: {genre.upper()}")
        print("="*70)
        
        # Auto-generate world
        world, locations, entities, config = generator.auto_generate_from_genre(genre)
        
        print(f"\n🌍 Thế giới: {world.name}")
        print(f"   Loại: {config['world_type']}")
        print(f"\n📊 Cấu hình:")
        print(f"   - Số người: {config['num_people']}")
        print(f"   - Có rừng: {'Có' if config['has_forests'] else 'Không'}")
        print(f"   - Số sông: {config['num_rivers']}")
        print(f"   - Số hồ: {config['num_lakes']}")
        print(f"   - Nguy hiểm sông: {config['river_danger']}/10")
        print(f"   - Nguy hiểm rừng: {config['forest_danger']}/10")
        print(f"   - Nguy hiểm hồ: {config['lake_danger']}/10")
        
        print(f"\n📍 Địa điểm ({len(locations)}):")
        for loc in locations[:5]:  # Show first 5
            print(f"   - {loc.name}: {loc.metadata.get('location_type', 'N/A')}")
        
        # Count dangerous entities
        dangerous_count = sum(1 for e in entities if e.attributes.get('is_dangerous', False))
        safe_count = len(entities) - dangerous_count
        
        print(f"\n👥 Thực thể ({len(entities)}):")
        print(f"   - Người: {safe_count}")
        print(f"   - Sinh vật nguy hiểm: {dangerous_count}")
        
        # Show sample entities
        print(f"\n   Ví dụ người:")
        for e in [e for e in entities if not e.attributes.get('is_dangerous', False)][:3]:
            print(f"      - {e.name} ({e.entity_type})")
        
        if dangerous_count > 0:
            print(f"\n   Ví dụ sinh vật nguy hiểm:")
            for e in [e for e in entities if e.attributes.get('is_dangerous', False)][:3]:
                threat = e.attributes.get('threat_level', 0)
                print(f"      - {e.name} ({e.entity_type}, threat: {threat}/10)")
        
        # Save to storage
        storage.save_world(world.to_dict())
        for loc in locations:
            storage.save_location(loc.to_dict())
        for ent in entities:
            storage.save_entity(ent.to_dict())
        
        # Create a sample story
        story = story_gen.generate(
            f"A {genre} story in {world.name}",
            world.world_id,
            genre,
            locations=[loc.location_id for loc in locations[:2]],
            entities=[ent.entity_id for ent in entities[:3]]
        )
        storage.save_story(story.to_dict())
        
        print(f"\n📖 Câu chuyện: {story.title}")
        print(f"   ID: {story.story_id}")
    
    print("\n" + "="*70)
    print("DEMO: Chỉnh sửa cấu hình")
    print("="*70)
    
    # Demo with custom configuration
    custom_config = {
        'num_people': 10,
        'has_forests': True,
        'num_rivers': 3,
        'num_lakes': 1,
        'river_danger': 8,
        'forest_danger': 9,
        'lake_danger': 3
    }
    
    print("\n⚙️ Cấu hình tùy chỉnh:")
    for key, value in custom_config.items():
        print(f"   - {key}: {value}")
    
    world, locations, entities, config = generator.auto_generate_from_genre(
        "adventure",
        name="Custom Dangerous World",
        editable_config=custom_config
    )
    
    print(f"\n🌍 Thế giới: {world.name}")
    print(f"\n📊 Kết quả:")
    print(f"   - Địa điểm: {len(locations)}")
    print(f"   - Thực thể: {len(entities)}")
    
    dangerous_count = sum(1 for e in entities if e.attributes.get('is_dangerous', False))
    print(f"   - Sinh vật nguy hiểm: {dangerous_count} (do danger levels cao)")
    
    print("\n✅ Demo hoàn thành!")
    print(f"\nDatabase: demo_auto.db")
    print(f"Tổng số thế giới: {len(storage.list_worlds())}")
    print(f"Tổng số câu chuyện: {len(storage.list_stories())}")


if __name__ == "__main__":
    demo_auto_generation()
