"""
Story Creator - Trình tạo thế giới và câu chuyện

Main entry point for the story creator application.
Provides both terminal and GUI interfaces.
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
        choices=["terminal", "gui"],
        default="terminal",
        help="Chọn giao diện: terminal hoặc gui (mặc định: terminal)"
    )
    parser.add_argument(
        "--data-dir",
        "-d",
        default="data",
        help="Thư mục lưu trữ dữ liệu (mặc định: data)"
    )
    
    args = parser.parse_args()
    
    if args.interface == "gui":
        from interfaces.gui_interface import GUIInterface
        app = GUIInterface(data_dir=args.data_dir)
        app.run()
    else:
        from interfaces.terminal_interface import TerminalInterface
        app = TerminalInterface(data_dir=args.data_dir)
        app.run()


if __name__ == "__main__":
    main()
