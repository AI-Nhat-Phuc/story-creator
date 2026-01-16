"""Terminal-based interface for the story creator system."""

import sys
from typing import Optional, List
from models import World, Story, Location, Entity, TimeCone
from generators import WorldGenerator, StoryGenerator, StoryLinker
from utils import Storage, NoSQLStorage


class TerminalInterface:
    """Terminal-based user interface for creating and managing worlds and stories."""
    
    def __init__(
        self,
        data_dir: str = "data",
        storage_type: str = "nosql",
        db_path: str = "story_creator.db"
    ):
        """
        Initialize the TerminalInterface.
        
        Args:
            data_dir: Directory to store data files (for JSON storage)
            storage_type: Type of storage ("json" or "nosql")
            db_path: Path to database file (for NoSQL storage)
        """
        # Initialize storage based on type
        if storage_type == "nosql":
            self.storage = NoSQLStorage(db_path)
            self.storage_type = "NoSQL"
        else:
            self.storage = Storage(data_dir)
            self.storage_type = "JSON"
        
        self.world_generator = WorldGenerator()
        self.story_generator = StoryGenerator()
        self.story_linker = StoryLinker()
        self.current_world: Optional[World] = None
    
    def run(self) -> None:
        """Run the main terminal interface loop."""
        print("\n" + "="*60)
        print("  STORY CREATOR - Terminal Interface")
        print("  Tạo thế giới và câu chuyện bằng Python")
        print(f"  Storage: {self.storage_type}")
        print("="*60 + "\n")
        
        while True:
            self.show_main_menu()
            choice = input("\nChọn tùy chọn (Enter số): ").strip()
            
            if choice == "1":
                self.create_world_menu()
            elif choice == "2":
                self.list_worlds_menu()
            elif choice == "3":
                self.select_world_menu()
            elif choice == "4":
                self.create_story_menu()
            elif choice == "5":
                self.list_stories_menu()
            elif choice == "6":
                self.link_stories_menu()
            elif choice == "7":
                self.view_world_details()
            elif choice == "0":
                print("\nCảm ơn bạn đã sử dụng Story Creator!")
                sys.exit(0)
            else:
                print("\n❌ Lựa chọn không hợp lệ. Vui lòng thử lại.")
    
    def show_main_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "-"*60)
        print("MENU CHÍNH")
        print("-"*60)
        print("1. Tạo thế giới mới")
        print("2. Xem danh sách thế giới")
        print("3. Chọn thế giới hiện tại")
        print("4. Tạo câu chuyện mới")
        print("5. Xem danh sách câu chuyện")
        print("6. Liên kết các câu chuyện")
        print("7. Xem chi tiết thế giới")
        print("0. Thoát")
        print("-"*60)
        
        if self.current_world:
            print(f"📍 Thế giới hiện tại: {self.current_world.name}")
    
    def create_world_menu(self) -> None:
        """Menu for creating a new world."""
        print("\n" + "="*60)
        print("TẠO THẾ GIỚI MỚI")
        print("="*60)
        
        print("\nChọn loại thế giới:")
        print("1. Fantasy (Giả tưởng)")
        print("2. Sci-Fi (Khoa học viễn tưởng)")
        print("3. Modern (Hiện đại)")
        print("4. Historical (Lịch sử)")
        
        world_type_choice = input("\nChọn loại (1-4): ").strip()
        world_types = {
            "1": "fantasy",
            "2": "sci-fi",
            "3": "modern",
            "4": "historical"
        }
        
        world_type = world_types.get(world_type_choice, "fantasy")
        
        prompt = input("\nMô tả thế giới của bạn: ").strip()
        
        if not prompt:
            print("❌ Mô tả không được để trống!")
            return
        
        # Generate world
        world = self.world_generator.generate(prompt, world_type)
        
        # Generate locations
        location_count = int(input("\nSố lượng địa điểm (mặc định 3): ").strip() or "3")
        locations = self.world_generator.generate_locations(world, location_count)
        
        # Generate entities
        entity_count = int(input("Số lượng thực thể (mặc định 3): ").strip() or "3")
        entities = self.world_generator.generate_entities(world, entity_count)
        
        # Save everything
        self.storage.save_world(world.to_dict())
        for location in locations:
            self.storage.save_location(location.to_dict())
        for entity in entities:
            self.storage.save_entity(entity.to_dict())
        
        print(f"\n✅ Đã tạo thế giới: {world.name}")
        print(f"   ID: {world.world_id}")
        print(f"   Loại: {world_type}")
        print(f"   Địa điểm: {len(locations)}")
        print(f"   Thực thể: {len(entities)}")
        
        self.current_world = world
    
    def list_worlds_menu(self) -> None:
        """Menu for listing all worlds."""
        print("\n" + "="*60)
        print("DANH SÁCH THẾ GIỚI")
        print("="*60)
        
        worlds = self.storage.list_worlds()
        
        if not worlds:
            print("\n❌ Chưa có thế giới nào. Hãy tạo thế giới mới!")
            return
        
        for i, world_data in enumerate(worlds, 1):
            print(f"\n{i}. {world_data['name']}")
            print(f"   ID: {world_data['world_id']}")
            print(f"   Mô tả: {world_data['description'][:100]}...")
            print(f"   Câu chuyện: {len(world_data.get('stories', []))}")
    
    def select_world_menu(self) -> None:
        """Menu for selecting current world."""
        worlds = self.storage.list_worlds()
        
        if not worlds:
            print("\n❌ Chưa có thế giới nào. Hãy tạo thế giới mới!")
            return
        
        print("\n" + "="*60)
        print("CHỌN THẾ GIỚI")
        print("="*60)
        
        for i, world_data in enumerate(worlds, 1):
            print(f"{i}. {world_data['name']}")
        
        choice = input("\nChọn thế giới (Enter số): ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(worlds):
                world_data = worlds[idx]
                self.current_world = World.from_dict(world_data)
                print(f"\n✅ Đã chọn thế giới: {self.current_world.name}")
            else:
                print("\n❌ Lựa chọn không hợp lệ!")
        except ValueError:
            print("\n❌ Vui lòng nhập số!")
    
    def create_story_menu(self) -> None:
        """Menu for creating a new story."""
        if not self.current_world:
            print("\n❌ Vui lòng chọn thế giới trước!")
            return
        
        print("\n" + "="*60)
        print("TẠO CÂU CHUYỆN MỚI")
        print("="*60)
        
        print("\nChọn thể loại:")
        print("1. Adventure (Phiêu lưu)")
        print("2. Mystery (Bí ẩn)")
        print("3. Conflict (Xung đột)")
        print("4. Discovery (Khám phá)")
        
        genre_choice = input("\nChọn thể loại (1-4): ").strip()
        genres = {
            "1": "adventure",
            "2": "mystery",
            "3": "conflict",
            "4": "discovery"
        }
        
        genre = genres.get(genre_choice, "adventure")
        
        prompt = input("\nMô tả câu chuyện: ").strip()
        
        if not prompt:
            print("❌ Mô tả không được để trống!")
            return
        
        # Generate story
        story = self.story_generator.generate(
            prompt,
            self.current_world.world_id,
            genre,
            locations=self.current_world.locations[:1] if self.current_world.locations else None,
            entities=self.current_world.entities[:1] if self.current_world.entities else None
        )
        
        # Generate time cone
        time_cone = self.story_generator.generate_time_cone(
            story,
            self.current_world.world_id
        )
        
        # Save
        self.storage.save_story(story.to_dict())
        self.storage.save_time_cone(time_cone.to_dict())
        
        # Update world
        self.current_world.add_story(story.story_id)
        self.storage.save_world(self.current_world.to_dict())
        
        print(f"\n✅ Đã tạo câu chuyện: {story.title}")
        print(f"   ID: {story.story_id}")
        print(f"   Thể loại: {genre}")
    
    def list_stories_menu(self) -> None:
        """Menu for listing all stories."""
        print("\n" + "="*60)
        print("DANH SÁCH CÂU CHUYỆN")
        print("="*60)
        
        world_id = self.current_world.world_id if self.current_world else None
        stories = self.storage.list_stories(world_id)
        
        if not stories:
            print("\n❌ Chưa có câu chuyện nào!")
            return
        
        for i, story_data in enumerate(stories, 1):
            print(f"\n{i}. {story_data['title']}")
            print(f"   ID: {story_data['story_id']}")
            print(f"   Nội dung: {story_data['content'][:100]}...")
            print(f"   Liên kết: {len(story_data.get('linked_stories', []))} câu chuyện")
    
    def link_stories_menu(self) -> None:
        """Menu for linking stories."""
        if not self.current_world:
            print("\n❌ Vui lòng chọn thế giới trước!")
            return
        
        print("\n" + "="*60)
        print("LIÊN KẾT CÂU CHUYỆN")
        print("="*60)
        
        # Load all stories in current world
        stories_data = self.storage.list_stories(self.current_world.world_id)
        
        if len(stories_data) < 2:
            print("\n❌ Cần ít nhất 2 câu chuyện để liên kết!")
            return
        
        stories = [Story.from_dict(s) for s in stories_data]
        
        print("\nChọn phương thức liên kết:")
        print("1. Theo thực thể chung")
        print("2. Theo địa điểm chung")
        print("3. Theo thời gian chung")
        print("4. Tất cả các phương thức")
        
        choice = input("\nChọn (1-4): ").strip()
        
        link_entities = choice in ["1", "4"]
        link_locations = choice in ["2", "4"]
        link_time = choice in ["3", "4"]
        
        # Link stories
        self.story_linker.link_stories(
            stories,
            link_by_entities=link_entities,
            link_by_locations=link_locations,
            link_by_time=link_time
        )
        
        # Save updated stories
        for story in stories:
            self.storage.save_story(story.to_dict())
        
        print("\n✅ Đã liên kết các câu chuyện!")
        
        # Show results
        for story in stories:
            if story.linked_stories:
                print(f"\n{story.title}: {len(story.linked_stories)} liên kết")
    
    def view_world_details(self) -> None:
        """View detailed information about current world."""
        if not self.current_world:
            print("\n❌ Vui lòng chọn thế giới trước!")
            return
        
        print("\n" + "="*60)
        print(f"CHI TIẾT THẾ GIỚI: {self.current_world.name}")
        print("="*60)
        
        print(f"\nID: {self.current_world.world_id}")
        print(f"Mô tả: {self.current_world.description}")
        print(f"\nSố lượng:")
        print(f"  - Câu chuyện: {len(self.current_world.stories)}")
        print(f"  - Địa điểm: {len(self.current_world.locations)}")
        print(f"  - Thực thể: {len(self.current_world.entities)}")
        
        if self.current_world.metadata:
            print(f"\nMetadata:")
            for key, value in self.current_world.metadata.items():
                print(f"  - {key}: {value}")


def main():
    """Main entry point for terminal interface."""
    interface = TerminalInterface()
    interface.run()


if __name__ == "__main__":
    main()
