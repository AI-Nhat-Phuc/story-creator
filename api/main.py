"""
Story Creator - Trình tạo thế giới và câu chuyện

Main entry point for the story creator application.
Provides API backend and character simulation mode.
"""

import sys
import os
import io
import logging
import argparse

# Ensure api/ is on sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Setup simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Story Creator - Tạo thế giới và câu chuyện bằng Python"
    )
    parser.add_argument(
        "--interface",
        "-i",
        choices=["api", "simulation"],
        default="api",
        help="Chọn giao diện: api (React backend), simulation (mặc định: api)"
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
    # Use /tmp for db path if running on Vercel (read-only filesystem workaround)
    vercel_db_path = os.environ.get("STORY_DB_PATH")
    default_db_path = vercel_db_path if vercel_db_path else "/tmp/story_creator.db" if os.environ.get("VERCEL") else "story_creator.db"
    parser.add_argument(
        "--db-path",
        default=default_db_path,
        help="Đường dẫn đến database (chỉ dùng cho NoSQL) (mặc định: story_creator.db, Vercel: /tmp/story_creator.db)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Bật chế độ debug logging (hiển thị tất cả log chi tiết)"
    )

    args = parser.parse_args()

    # Setup logging based on debug flag
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.getLogger().setLevel(log_level)
    logger = logging.getLogger(__name__)

    logger.info("=== Story Creator Starting ===")
    if args.debug:
        logger.debug("Debug mode enabled")

    logger.info(f"Interface: {args.interface}, Storage: {args.storage}")

    if args.interface == "simulation":
        # Character simulation mode
        logger.info("Launching simulation mode")
        from interfaces.simulation_interface import main as sim_main
        sim_main()
    elif args.interface == "api":
        # Pure API backend for React frontend
        logger.info("Launching API Backend")
        from interfaces.api_backend import APIBackend
        api = APIBackend(
            data_dir=args.data_dir,
            storage_type=args.storage,
            db_path=args.db_path
        )
        api.run(host='127.0.0.1', port=5000, debug=args.debug)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
