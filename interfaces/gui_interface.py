"""GUI-based interface for the story creator system using tkinter."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Optional, List
from models import World, Story
from generators import WorldGenerator, StoryGenerator, StoryLinker
from utils import Storage


class GUIInterface:
    """Graphical user interface for creating and managing worlds and stories."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the GUIInterface.
        
        Args:
            data_dir: Directory to store data files
        """
        self.storage = Storage(data_dir)
        self.world_generator = WorldGenerator()
        self.story_generator = StoryGenerator()
        self.story_linker = StoryLinker()
        self.current_world: Optional[World] = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Story Creator - Trình tạo thế giới và câu chuyện")
        self.root.geometry("900x700")
        
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Set up the user interface."""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_world_tab()
        self.create_story_tab()
        self.create_view_tab()
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Sẵn sàng",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_world_tab(self) -> None:
        """Create the world creation tab."""
        world_frame = ttk.Frame(self.notebook)
        self.notebook.add(world_frame, text="Tạo thế giới")
        
        # Title
        title_label = tk.Label(
            world_frame,
            text="Tạo thế giới mới",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # World type selection
        type_frame = ttk.LabelFrame(world_frame, text="Loại thế giới", padding=10)
        type_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.world_type_var = tk.StringVar(value="fantasy")
        
        types = [
            ("Fantasy (Giả tưởng)", "fantasy"),
            ("Sci-Fi (Khoa học viễn tưởng)", "sci-fi"),
            ("Modern (Hiện đại)", "modern"),
            ("Historical (Lịch sử)", "historical")
        ]
        
        for text, value in types:
            rb = ttk.Radiobutton(
                type_frame,
                text=text,
                variable=self.world_type_var,
                value=value
            )
            rb.pack(anchor=tk.W)
        
        # World description
        desc_frame = ttk.LabelFrame(world_frame, text="Mô tả thế giới", padding=10)
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.world_desc_text = scrolledtext.ScrolledText(
            desc_frame,
            height=5,
            wrap=tk.WORD
        )
        self.world_desc_text.pack(fill=tk.BOTH, expand=True)
        
        # Options
        options_frame = ttk.Frame(world_frame)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(options_frame, text="Số địa điểm:").pack(side=tk.LEFT, padx=5)
        self.location_count_var = tk.StringVar(value="3")
        location_spinbox = ttk.Spinbox(
            options_frame,
            from_=1,
            to=10,
            textvariable=self.location_count_var,
            width=5
        )
        location_spinbox.pack(side=tk.LEFT, padx=5)
        
        tk.Label(options_frame, text="Số thực thể:").pack(side=tk.LEFT, padx=5)
        self.entity_count_var = tk.StringVar(value="3")
        entity_spinbox = ttk.Spinbox(
            options_frame,
            from_=1,
            to=10,
            textvariable=self.entity_count_var,
            width=5
        )
        entity_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Create button
        create_btn = ttk.Button(
            world_frame,
            text="Tạo thế giới",
            command=self.create_world
        )
        create_btn.pack(pady=10)
    
    def create_story_tab(self) -> None:
        """Create the story creation tab."""
        story_frame = ttk.Frame(self.notebook)
        self.notebook.add(story_frame, text="Tạo câu chuyện")
        
        # Title
        title_label = tk.Label(
            story_frame,
            text="Tạo câu chuyện mới",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # World selection
        world_select_frame = ttk.LabelFrame(story_frame, text="Chọn thế giới", padding=10)
        world_select_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.world_combo = ttk.Combobox(world_select_frame, state="readonly")
        self.world_combo.pack(fill=tk.X)
        self.world_combo.bind("<<ComboboxSelected>>", self.on_world_selected)
        
        refresh_btn = ttk.Button(
            world_select_frame,
            text="Làm mới danh sách",
            command=self.refresh_worlds
        )
        refresh_btn.pack(pady=5)
        
        # Genre selection
        genre_frame = ttk.LabelFrame(story_frame, text="Thể loại", padding=10)
        genre_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.story_genre_var = tk.StringVar(value="adventure")
        
        genres = [
            ("Adventure (Phiêu lưu)", "adventure"),
            ("Mystery (Bí ẩn)", "mystery"),
            ("Conflict (Xung đột)", "conflict"),
            ("Discovery (Khám phá)", "discovery")
        ]
        
        for text, value in genres:
            rb = ttk.Radiobutton(
                genre_frame,
                text=text,
                variable=self.story_genre_var,
                value=value
            )
            rb.pack(anchor=tk.W)
        
        # Story description
        desc_frame = ttk.LabelFrame(story_frame, text="Mô tả câu chuyện", padding=10)
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.story_desc_text = scrolledtext.ScrolledText(
            desc_frame,
            height=5,
            wrap=tk.WORD
        )
        self.story_desc_text.pack(fill=tk.BOTH, expand=True)
        
        # Create button
        create_btn = ttk.Button(
            story_frame,
            text="Tạo câu chuyện",
            command=self.create_story
        )
        create_btn.pack(pady=10)
        
        # Link stories button
        link_btn = ttk.Button(
            story_frame,
            text="Liên kết các câu chuyện",
            command=self.link_stories
        )
        link_btn.pack(pady=5)
    
    def create_view_tab(self) -> None:
        """Create the view/browse tab."""
        view_frame = ttk.Frame(self.notebook)
        self.notebook.add(view_frame, text="Xem dữ liệu")
        
        # Title
        title_label = tk.Label(
            view_frame,
            text="Xem thế giới và câu chuyện",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Worlds list
        worlds_frame = ttk.LabelFrame(view_frame, text="Danh sách thế giới", padding=10)
        worlds_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.worlds_listbox = tk.Listbox(worlds_frame, height=5)
        self.worlds_listbox.pack(fill=tk.BOTH, expand=True)
        self.worlds_listbox.bind("<<ListboxSelect>>", self.on_world_list_selected)
        
        # Stories list
        stories_frame = ttk.LabelFrame(view_frame, text="Danh sách câu chuyện", padding=10)
        stories_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.stories_listbox = tk.Listbox(stories_frame, height=5)
        self.stories_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Details text
        details_frame = ttk.LabelFrame(view_frame, text="Chi tiết", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.details_text = scrolledtext.ScrolledText(
            details_frame,
            height=8,
            wrap=tk.WORD
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        refresh_btn = ttk.Button(
            view_frame,
            text="Làm mới",
            command=self.refresh_view
        )
        refresh_btn.pack(pady=10)
    
    def create_world(self) -> None:
        """Handle world creation."""
        world_type = self.world_type_var.get()
        description = self.world_desc_text.get("1.0", tk.END).strip()
        
        if not description:
            messagebox.showerror("Lỗi", "Vui lòng nhập mô tả thế giới!")
            return
        
        try:
            location_count = int(self.location_count_var.get())
            entity_count = int(self.entity_count_var.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng không hợp lệ!")
            return
        
        # Generate world
        world = self.world_generator.generate(description, world_type)
        locations = self.world_generator.generate_locations(world, location_count)
        entities = self.world_generator.generate_entities(world, entity_count)
        
        # Save
        self.storage.save_world(world.to_dict())
        for location in locations:
            self.storage.save_location(location.to_dict())
        for entity in entities:
            self.storage.save_entity(entity.to_dict())
        
        self.current_world = world
        
        messagebox.showinfo(
            "Thành công",
            f"Đã tạo thế giới: {world.name}\n"
            f"Địa điểm: {len(locations)}\n"
            f"Thực thể: {len(entities)}"
        )
        
        self.status_bar.config(text=f"Thế giới hiện tại: {world.name}")
        self.refresh_worlds()
        self.refresh_view()
    
    def create_story(self) -> None:
        """Handle story creation."""
        if not self.current_world:
            messagebox.showerror("Lỗi", "Vui lòng chọn thế giới trước!")
            return
        
        genre = self.story_genre_var.get()
        description = self.story_desc_text.get("1.0", tk.END).strip()
        
        if not description:
            messagebox.showerror("Lỗi", "Vui lòng nhập mô tả câu chuyện!")
            return
        
        # Generate story
        story = self.story_generator.generate(
            description,
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
        
        messagebox.showinfo("Thành công", f"Đã tạo câu chuyện: {story.title}")
        self.refresh_view()
    
    def link_stories(self) -> None:
        """Handle story linking."""
        if not self.current_world:
            messagebox.showerror("Lỗi", "Vui lòng chọn thế giới trước!")
            return
        
        stories_data = self.storage.list_stories(self.current_world.world_id)
        
        if len(stories_data) < 2:
            messagebox.showerror("Lỗi", "Cần ít nhất 2 câu chuyện để liên kết!")
            return
        
        stories = [Story.from_dict(s) for s in stories_data]
        
        # Link all stories
        self.story_linker.link_stories(
            stories,
            link_by_entities=True,
            link_by_locations=True,
            link_by_time=True
        )
        
        # Save updated stories
        for story in stories:
            self.storage.save_story(story.to_dict())
        
        messagebox.showinfo("Thành công", "Đã liên kết các câu chuyện!")
        self.refresh_view()
    
    def refresh_worlds(self) -> None:
        """Refresh the worlds combobox."""
        worlds = self.storage.list_worlds()
        world_names = [f"{w['name']} ({w['world_id'][:8]})" for w in worlds]
        
        self.world_combo['values'] = world_names
        if world_names:
            self.world_combo.current(0)
            self.on_world_selected(None)
    
    def on_world_selected(self, event) -> None:
        """Handle world selection from combobox."""
        selection = self.world_combo.get()
        if not selection:
            return
        
        # Extract world_id from selection
        world_id = selection.split('(')[-1].rstrip(')')
        
        # Find full world
        worlds = self.storage.list_worlds()
        for world_data in worlds:
            if world_data['world_id'].startswith(world_id):
                self.current_world = World.from_dict(world_data)
                self.status_bar.config(text=f"Thế giới hiện tại: {self.current_world.name}")
                break
    
    def refresh_view(self) -> None:
        """Refresh the view tab."""
        # Refresh worlds list
        self.worlds_listbox.delete(0, tk.END)
        worlds = self.storage.list_worlds()
        for world_data in worlds:
            self.worlds_listbox.insert(
                tk.END,
                f"{world_data['name']} - {len(world_data.get('stories', []))} câu chuyện"
            )
        
        # Refresh stories list if world selected
        if self.current_world:
            self.stories_listbox.delete(0, tk.END)
            stories = self.storage.list_stories(self.current_world.world_id)
            for story_data in stories:
                self.stories_listbox.insert(
                    tk.END,
                    f"{story_data['title']} ({story_data.get('metadata', {}).get('genre', 'N/A')})"
                )
    
    def on_world_list_selected(self, event) -> None:
        """Handle world selection from listbox."""
        selection = self.worlds_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        worlds = self.storage.list_worlds()
        
        if idx < len(worlds):
            world_data = worlds[idx]
            self.current_world = World.from_dict(world_data)
            
            # Update details
            details = f"Thế giới: {world_data['name']}\n"
            details += f"ID: {world_data['world_id']}\n"
            details += f"Mô tả: {world_data['description']}\n"
            details += f"Câu chuyện: {len(world_data.get('stories', []))}\n"
            details += f"Địa điểm: {len(world_data.get('locations', []))}\n"
            details += f"Thực thể: {len(world_data.get('entities', []))}\n"
            
            self.details_text.delete("1.0", tk.END)
            self.details_text.insert("1.0", details)
            
            # Refresh stories for this world
            self.stories_listbox.delete(0, tk.END)
            stories = self.storage.list_stories(self.current_world.world_id)
            for story_data in stories:
                self.stories_listbox.insert(
                    tk.END,
                    f"{story_data['title']} ({story_data.get('metadata', {}).get('genre', 'N/A')})"
                )
    
    def run(self) -> None:
        """Run the GUI application."""
        self.refresh_worlds()
        self.refresh_view()
        self.root.mainloop()


def main():
    """Main entry point for GUI interface."""
    app = GUIInterface()
    app.run()


if __name__ == "__main__":
    main()
