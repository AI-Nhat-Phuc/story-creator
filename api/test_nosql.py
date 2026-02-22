#!/usr/bin/env python
"""Test script for NoSQL storage implementation."""

import sys
import os
import tempfile

# Set TEST_MODE to allow database clearing
os.environ['TEST_MODE'] = '1'

from core.models import World, Story, Location, Entity, TimeCone
from generators import WorldGenerator, StoryGenerator, StoryLinker
from storage.nosql_storage import NoSQLStorage


def test_nosql_basic_operations():
    """Test basic NoSQL operations."""
    print("Testing NoSQL basic operations...")

    # Use temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_db.name
    temp_db.close()

    try:
        storage = NoSQLStorage(temp_db_path)
        storage.clear_all()

        # Test world storage (create public world for testing)
        world = World(name="Test World", description="Test", visibility="public")
        storage.save_world(world.to_dict())
        loaded_world = storage.load_world(world.world_id)
        assert loaded_world is not None
        assert loaded_world["name"] == "Test World"

        # Test story storage (create public story)
        story = Story(title="Test Story", content="Test", world_id=world.world_id, visibility="public")
        storage.save_story(story.to_dict())
        loaded_story = storage.load_story(story.story_id)
        assert loaded_story is not None
        assert loaded_story["title"] == "Test Story"

        # Test list operations (without user_id, should return public items only)
        worlds = storage.list_worlds()
        assert len(worlds) >= 1, f"Expected at least 1 world, got {len(worlds)}"

        stories = storage.list_stories()
        assert len(stories) >= 1, f"Expected at least 1 story, got {len(stories)}"

        # Test filtered list
        filtered_stories = storage.list_stories(world.world_id)
        assert len(filtered_stories) >= 1
        assert filtered_stories[0]["world_id"] == world.world_id

        # Test stats
        stats = storage.get_stats()
        print(f"   DEBUG: Stats = {stats}")
        assert stats["worlds"] >= 1
        assert stats["stories"] >= 1

        print("✅ NoSQL basic operations passed")

    finally:
        try:
            storage.close()
        except:
            pass
        # Clean up
        if os.path.exists(temp_db_path):
            try:
                os.unlink(temp_db_path)
            except PermissionError:
                print(f"   ⚠️  Could not delete temp file: {temp_db_path}")


def test_nosql_update_operations():
    """Test NoSQL update operations."""
    print("\nTesting NoSQL update operations...")

    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_db.name
    temp_db.close()

    try:
        storage = NoSQLStorage(temp_db_path)
        storage.clear_all()

        # Create and save world (public for testing)
        world = World(name="Original Name", description="Original", visibility="public")
        storage.save_world(world.to_dict())

        # Update world
        world.name = "Updated Name"
        world.metadata["updated"] = True
        storage.save_world(world.to_dict())

        # Verify update
        loaded = storage.load_world(world.world_id)
        assert loaded["name"] == "Updated Name"
        assert loaded["metadata"]["updated"] == True

        # Verify only one entry exists
        worlds = storage.list_worlds()
        assert len(worlds) == 1

        print("✅ NoSQL update operations passed")

    finally:
        try:
            storage.close()
        except:
            pass
        if os.path.exists(temp_db_path):
            try:
                os.unlink(temp_db_path)
            except PermissionError:
                print(f"   ⚠️  Could not delete temp file: {temp_db_path}")


def test_nosql_delete_operations():
    """Test NoSQL delete operations."""
    print("\nTesting NoSQL delete operations...")

    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_db.name
    temp_db.close()

    try:
        storage = NoSQLStorage(temp_db_path)
        storage.clear_all()

        # Create multiple worlds (public for testing)
        world1 = World(name="World 1", description="Test 1", visibility="public")
        world2 = World(name="World 2", description="Test 2", visibility="public")

        storage.save_world(world1.to_dict())
        storage.save_world(world2.to_dict())

        assert len(storage.list_worlds()) == 2

        # Delete one world
        result = storage.delete_world(world1.world_id)
        assert result == True
        assert len(storage.list_worlds()) == 1

        # Try to delete non-existent world
        result = storage.delete_world("non-existent-id")
        assert result == False

        print("✅ NoSQL delete operations passed")

    finally:
        try:
            storage.close()
        except:
            pass
        if os.path.exists(temp_db_path):
            try:
                os.unlink(temp_db_path)
            except PermissionError:
                print(f"   ⚠️  Could not delete temp file: {temp_db_path}")


def test_nosql_with_generators():
    """Test NoSQL with generators."""
    print("\nTesting NoSQL with generators...")

    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_db.name
    temp_db.close()

    try:
        storage = NoSQLStorage(temp_db_path)
        storage.clear_all()

        world_gen = WorldGenerator()
        story_gen = StoryGenerator()

        # Generate world with locations and entities (public for testing)
        world = world_gen.generate("Test world", "fantasy")
        world.visibility = "public"  # Set public for testing
        locations = world_gen.generate_locations(world, 3)
        entities = world_gen.generate_entities(world, 3)

        # Save to database
        storage.save_world(world.to_dict())
        for loc in locations:
            storage.save_location(loc.to_dict())
        for ent in entities:
            storage.save_entity(ent.to_dict())

        # Verify
        stats = storage.get_stats()
        assert stats["worlds"] == 1
        assert stats["locations"] == 3
        assert stats["entities"] == 3

        # Generate and save story (public for testing)
        story = story_gen.generate(
            title="Test Story",
            description="Test story description",
            world_id=world.world_id,
            genre="adventure"
        )
        story.visibility = "public"  # Set public for testing
        storage.save_story(story.to_dict())

        # Verify story
        loaded_story = storage.load_story(story.story_id)
        assert loaded_story is not None
        assert loaded_story["world_id"] == world.world_id

        print("✅ NoSQL with generators passed")

    finally:
        try:
            storage.close()
        except:
            pass
        if os.path.exists(temp_db_path):
            try:
                os.unlink(temp_db_path)
            except PermissionError:
                print(f"   ⚠️  Could not delete temp file: {temp_db_path}")


def test_nosql_performance():
    """Test NoSQL performance with larger dataset."""
    print("\nTesting NoSQL performance...")

    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_db.name
    temp_db.close()

    try:
        import time

        storage = NoSQLStorage(temp_db_path)
        storage.clear_all()

        # Create 100 worlds (public for testing)
        start = time.time()
        worlds = []
        for i in range(100):
            world = World(name=f"World {i}", description=f"Description {i}", visibility="public")
            storage.save_world(world.to_dict())
            worlds.append(world)

        write_time = time.time() - start

        # Query all worlds
        start = time.time()
        all_worlds = storage.list_worlds()
        query_time = time.time() - start

        assert len(all_worlds) == 100

        # Load specific worlds
        start = time.time()
        for world in worlds[:10]:
            loaded = storage.load_world(world.world_id)
            assert loaded is not None
        load_time = time.time() - start

        print(f"   - Write 100 worlds: {write_time:.4f}s")
        print(f"   - Query all worlds: {query_time:.4f}s")
        print(f"   - Load 10 worlds: {load_time:.4f}s")

        print("✅ NoSQL performance test passed")

    finally:
        try:
            storage.close()
        except:
            pass
        if os.path.exists(temp_db_path):
            try:
                os.unlink(temp_db_path)
            except PermissionError:
                print(f"   ⚠️  Could not delete temp file: {temp_db_path}")


def main():
    """Run all NoSQL tests."""
    print("="*70)
    print("  NoSQL STORAGE - TEST SUITE")
    print("="*70 + "\n")

    try:
        test_nosql_basic_operations()
        test_nosql_update_operations()
        test_nosql_delete_operations()
        test_nosql_with_generators()
        test_nosql_performance()

        print("\n" + "="*70)
        print("  ✅ ALL NOSQL TESTS PASSED")
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
