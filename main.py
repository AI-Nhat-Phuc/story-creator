"""
Story Creator - Trình tạo thế giới và câu chuyện

Main entry point for the story creator application.
Provides both terminal and GUI interfaces, plus character simulation mode.
"""

import sys
import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Story Creator - Tạo thế giới và câu chuyện bằng Python"
    )
    parser.add_argument(
        "--interface",
        "-i",
        choices=["terminal", "gui", "simulation"],
        default="terminal",
        help="Chọn giao diện: terminal, gui, hoặc simulation (mặc định: terminal)"
    )
    parser.add_argument(
        "--data-dir",
        "-d",
        default="data",
        help="Thư mục lưu trữ dữ liệu (chỉ dùng cho JSON) (mặc định: data)"
    )
    parser.add_argument(
        "--storage",
        "-s",
        choices=["json", "nosql"],
        default="nosql",
        help="Loại storage: json (file-based) hoặc nosql (database) (mặc định: nosql)"
    )
    parser.add_argument(
        "--db-path",
        default="story_creator.db",
        help="Đường dẫn đến database (chỉ dùng cho NoSQL) (mặc định: story_creator.db)"
    )
    
    args = parser.parse_args()
    
    if args.interface == "simulation":
        # Character simulation mode
        from interfaces.simulation_interface import main as sim_main
        sim_main()
    elif args.interface == "gui":
        from interfaces.gui_interface import GUIInterface
        app = GUIInterface(
            data_dir=args.data_dir,
            storage_type=args.storage,
            db_path=args.db_path
        )
        app.run()
    else:
        from interfaces.terminal_interface import TerminalInterface
        app = TerminalInterface(
            data_dir=args.data_dir,
            storage_type=args.storage,
            db_path=args.db_path
        )
        app.run()


if __name__ == "__main__":
    main()
