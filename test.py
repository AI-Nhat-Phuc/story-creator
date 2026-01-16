#!/usr/bin/env python
"""Test script to verify all functionality."""

import sys
import tempfile
import shutil
from models import World, Story, Location, Entity, TimeCone
from generators import WorldGenerator, StoryGenerator, StoryLinker
from utils import Storage


def test_models():
    """Test all data models."""
    print("Testing data models...")
    
    # Test World
    world = World(
        name="Test World",
        description="A test world"
    )
    assert world.world_id is not None
    assert world.name == "Test World"
    world_dict = world.to_dict()
    assert world_dict["type"] == "world"
    world2 = World.from_dict(world_dict)
    assert world2.world_id == world.world_id
    
    # Test Story
    story = Story(
        title="Test Story",
        content="Test content",
        world_id=world.world_id
    )
    assert story.story_id is not None
    story_dict = story.to_dict()
    assert story_dict["type"] == "story"
    story2 = Story.from_dict(story_dict)
    assert story2.story_id == story.story_id
    
    # Test Location
    location = Location(
        name="Test Location",
        description="Test location",
        world_id=world.world_id
    )
    assert location.location_id is not None
    location_dict = location.to_dict()
    assert location_dict["type"] == "location"
    
    # Test Entity
    entity = Entity(
        name="Test Entity",
        entity_type="character",
        description="Test entity",
        world_id=world.world_id
    )
    assert entity.entity_id is not None
    entity_dict = entity.to_dict()
    assert entity_dict["type"] == "entity"
    
    # Test TimeCone
    time_cone = TimeCone(
        name="Test Time Cone",
        description="Test time cone",
        world_id=world.world_id
    )
    assert time_cone.time_cone_id is not None
    time_cone_dict = time_cone.to_dict()
    assert time_cone_dict["type"] == "time_cone"
    
    print("✅ All models passed")


def test_storage():
    """Test storage functionality."""
    print("\nTesting storage...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        storage = Storage(temp_dir)
        
        # Test world storage
        world = World(name="Test World", description="Test")
        storage.save_world(world.to_dict())
        loaded_world = storage.load_world(world.world_id)
        assert loaded_world is not None
        assert loaded_world["name"] == "Test World"
        
        # Test story storage
        story = Story(title="Test Story", content="Test", world_id=world.world_id)
        storage.save_story(story.to_dict())
        loaded_story = storage.load_story(story.story_id)
        assert loaded_story is not None
        assert loaded_story["title"] == "Test Story"
        
        # Test list operations
        worlds = storage.list_worlds()
        assert len(worlds) == 1
        
        stories = storage.list_stories()
        assert len(stories) == 1
        
        print("✅ Storage passed")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_generators():
    """Test generators."""
    print("\nTesting generators...")
    
    # Test WorldGenerator
    world_gen = WorldGenerator()
    world = world_gen.generate(
        prompt="A magical fantasy world",
        world_type="fantasy"
    )
    assert world.name is not None
    assert "fantasy" in world.metadata.get("world_type", "")
    
    locations = world_gen.generate_locations(world, count=2)
    assert len(locations) == 2
    assert all(loc.world_id == world.world_id for loc in locations)
    
    entities = world_gen.generate_entities(world, count=2)
    assert len(entities) == 2
    assert all(ent.world_id == world.world_id for ent in entities)
    
    # Test StoryGenerator
    story_gen = StoryGenerator()
    story = story_gen.generate(
        prompt="A hero's journey",
        world_id=world.world_id,
        genre="adventure"
    )
    assert story.title is not None
    assert story.world_id == world.world_id
    
    time_cone = story_gen.generate_time_cone(story, world.world_id)
    assert time_cone.world_id == world.world_id
    
    print("✅ Generators passed")


def test_story_linker():
    """Test story linking."""
    print("\nTesting story linker...")
    
    world = World(name="Test World", description="Test")
    
    # Create stories with shared elements
    location_id = "loc-123"
    entity_id = "ent-456"
    
    story1 = Story(
        title="Story 1",
        content="Content 1",
        world_id=world.world_id
    )
    story1.add_location(location_id)
    story1.add_entity(entity_id)
    
    story2 = Story(
        title="Story 2",
        content="Content 2",
        world_id=world.world_id
    )
    story2.add_location(location_id)
    
    story3 = Story(
        title="Story 3",
        content="Content 3",
        world_id=world.world_id
    )
    story3.add_entity(entity_id)
    
    stories = [story1, story2, story3]
    
    # Test linking
    linker = StoryLinker()
    linker.link_stories(stories)
    
    # Verify links
    assert len(story1.linked_stories) > 0
    assert len(story2.linked_stories) > 0
    assert len(story3.linked_stories) > 0
    
    # Test graph
    graph = linker.get_story_graph(stories)
    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) > 0
    
    print("✅ Story linker passed")


def test_json_serialization():
    """Test JSON serialization with Vietnamese characters."""
    print("\nTesting JSON serialization...")
    
    world = World(
        name="Thế giới ma thuật",
        description="Một thế giới với nhiều phép thuật và rồng"
    )
    
    json_str = world.to_json()
    assert "Thế giới ma thuật" in json_str
    assert "phép thuật" in json_str
    
    # Test deserialization
    world2 = World.from_json(json_str)
    assert world2.name == world.name
    assert world2.description == world.description
    
    print("✅ JSON serialization passed")


def main():
    """Run all tests."""
    print("="*70)
    print("  STORY CREATOR - TEST SUITE")
    print("="*70 + "\n")
    
    try:
        test_models()
        test_storage()
        test_generators()
        test_story_linker()
        test_json_serialization()
        
        print("\n" + "="*70)
        print("  ✅ ALL TESTS PASSED")
        print("="*70)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
