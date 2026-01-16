#!/usr/bin/env python
"""Demo script to showcase the story creator functionality."""

from models import World, Story, Location, Entity, TimeCone
from generators import WorldGenerator, StoryGenerator, StoryLinker
from utils import Storage
import json


def print_section(title):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def main():
    """Run the demo."""
    print_section("STORY CREATOR - DEMO")
    
    # Initialize components
    storage = Storage("demo_data")
    world_gen = WorldGenerator()
    story_gen = StoryGenerator()
    story_linker = StoryLinker()
    
    # 1. Create a Fantasy World
    print_section("1. Tạo thế giới Fantasy")
    
    world = world_gen.generate(
        prompt="Một thế giới ma thuật với các vương quốc cổ xưa và rồng huyền thoại",
        world_type="fantasy"
    )
    
    print(f"✅ Đã tạo thế giới: {world.name}")
    print(f"   ID: {world.world_id}")
    print(f"   Loại: {world.metadata.get('world_type')}")
    print(f"   Mô tả: {world.description}")
    
    # Save world
    storage.save_world(world.to_dict())
    
    # 2. Generate locations
    print_section("2. Tạo địa điểm")
    
    locations = world_gen.generate_locations(world, count=3)
    
    for i, location in enumerate(locations, 1):
        print(f"{i}. {location.name}")
        print(f"   ID: {location.location_id}")
        print(f"   Mô tả: {location.description}")
        print(f"   Tọa độ: x={location.coordinates['x']:.2f}, y={location.coordinates['y']:.2f}")
        storage.save_location(location.to_dict())
    
    # 3. Generate entities
    print_section("3. Tạo thực thể")
    
    entities = world_gen.generate_entities(world, count=3)
    
    for i, entity in enumerate(entities, 1):
        print(f"{i}. {entity.name} ({entity.entity_type})")
        print(f"   ID: {entity.entity_id}")
        print(f"   Mô tả: {entity.description}")
        print(f"   Thuộc tính: Strength={entity.attributes['strength']}, "
              f"Intelligence={entity.attributes['intelligence']}, "
              f"Charisma={entity.attributes['charisma']}")
        storage.save_entity(entity.to_dict())
    
    # 4. Create stories
    print_section("4. Tạo câu chuyện")
    
    stories = []
    
    # Story 1
    story1 = story_gen.generate(
        prompt="Một hiệp sĩ trẻ bắt đầu cuộc hành trình tìm kiếm thanh kiếm huyền thoại",
        world_id=world.world_id,
        genre="adventure",
        locations=[locations[0].location_id] if locations else None,
        entities=[entities[0].entity_id] if entities else None
    )
    
    time_cone1 = story_gen.generate_time_cone(story1, world.world_id, "The Quest Begins")
    
    stories.append(story1)
    world.add_story(story1.story_id)
    storage.save_story(story1.to_dict())
    storage.save_time_cone(time_cone1.to_dict())
    
    print(f"1. {story1.title}")
    print(f"   ID: {story1.story_id}")
    print(f"   Thể loại: {story1.metadata.get('genre')}")
    print(f"   Nội dung: {story1.content[:150]}...")
    
    # Story 2
    story2 = story_gen.generate(
        prompt="Một phù thủy cổ đại khám phá ra bí mật của ma thuật đen tối",
        world_id=world.world_id,
        genre="mystery",
        locations=[locations[1].location_id] if len(locations) > 1 else None,
        entities=[entities[1].entity_id] if len(entities) > 1 else None
    )
    
    time_cone2 = story_gen.generate_time_cone(story2, world.world_id, "The Discovery")
    
    stories.append(story2)
    world.add_story(story2.story_id)
    storage.save_story(story2.to_dict())
    storage.save_time_cone(time_cone2.to_dict())
    
    print(f"\n2. {story2.title}")
    print(f"   ID: {story2.story_id}")
    print(f"   Thể loại: {story2.metadata.get('genre')}")
    print(f"   Nội dung: {story2.content[:150]}...")
    
    # Story 3 - share some entities with story 1
    story3 = story_gen.generate(
        prompt="Cuộc chiến giữa các vương quốc vì quyền lực tối thượng",
        world_id=world.world_id,
        genre="conflict",
        locations=[locations[0].location_id, locations[2].location_id] if len(locations) > 2 else None,
        entities=[entities[0].entity_id, entities[2].entity_id] if len(entities) > 2 else None
    )
    
    time_cone3 = story_gen.generate_time_cone(story3, world.world_id, "The Great War")
    
    stories.append(story3)
    world.add_story(story3.story_id)
    storage.save_story(story3.to_dict())
    storage.save_time_cone(time_cone3.to_dict())
    
    print(f"\n3. {story3.title}")
    print(f"   ID: {story3.story_id}")
    print(f"   Thể loại: {story3.metadata.get('genre')}")
    print(f"   Nội dung: {story3.content[:150]}...")
    
    # Update world
    storage.save_world(world.to_dict())
    
    # 5. Link stories
    print_section("5. Liên kết các câu chuyện")
    
    story_linker.link_stories(
        stories,
        link_by_entities=True,
        link_by_locations=True,
        link_by_time=True
    )
    
    # Save updated stories
    for story in stories:
        storage.save_story(story.to_dict())
    
    print("Kết quả liên kết:")
    for story in stories:
        print(f"\n{story.title}:")
        print(f"  - Số liên kết: {len(story.linked_stories)}")
        if story.linked_stories:
            print(f"  - Liên kết với: {story.linked_stories}")
    
    # 6. Show story graph
    print_section("6. Đồ thị liên kết câu chuyện")
    
    graph = story_linker.get_story_graph(stories)
    
    print("Nodes:")
    for node in graph["nodes"]:
        print(f"  - {node['title']} ({node['id'][:8]})")
    
    print("\nEdges (Liên kết):")
    for edge in graph["edges"]:
        from_story = next(s for s in stories if s.story_id == edge["from"])
        to_story = next(s for s in stories if s.story_id == edge["to"])
        print(f"  - {from_story.title} → {to_story.title}")
    
    # 7. Show JSON examples
    print_section("7. Ví dụ JSON")
    
    print("World JSON:")
    print(json.dumps(world.to_dict(), indent=2, ensure_ascii=False)[:500] + "...")
    
    print("\n\nStory JSON:")
    print(json.dumps(story1.to_dict(), indent=2, ensure_ascii=False)[:500] + "...")
    
    print("\n\nLocation JSON:")
    print(json.dumps(locations[0].to_dict(), indent=2, ensure_ascii=False)[:300] + "...")
    
    print("\n\nEntity JSON:")
    print(json.dumps(entities[0].to_dict(), indent=2, ensure_ascii=False)[:300] + "...")
    
    print("\n\nTime Cone JSON:")
    print(json.dumps(time_cone1.to_dict(), indent=2, ensure_ascii=False)[:300] + "...")
    
    # 8. Summary
    print_section("8. Tóm tắt")
    
    print(f"✅ Thế giới: {world.name}")
    print(f"   - Câu chuyện: {len(world.stories)}")
    print(f"   - Địa điểm: {len(world.locations)}")
    print(f"   - Thực thể: {len(world.entities)}")
    print(f"\n📁 Dữ liệu đã được lưu vào thư mục: demo_data/")
    print(f"   - demo_data/worlds/{world.world_id}.json")
    print(f"   - demo_data/stories/ ({len(stories)} files)")
    print(f"   - demo_data/locations/ ({len(locations)} files)")
    print(f"   - demo_data/entities/ ({len(entities)} files)")
    print(f"   - demo_data/time_cones/ ({len(stories)} files)")
    
    print_section("DEMO HOÀN THÀNH")
    print("Bạn có thể khám phá dữ liệu JSON trong thư mục demo_data/")
    print("Chạy ứng dụng với: python main.py -i terminal hoặc python main.py -i gui")


if __name__ == "__main__":
    main()
