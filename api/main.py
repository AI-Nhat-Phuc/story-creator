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
    # Compute db path based on APP_ENV (production|staging|development)
    _env = os.environ.get("APP_ENV", "development").lower()
    _env_suffix = {"production": "_prod", "staging": "_staging"}.get(_env, "")
    _is_vercel = os.environ.get("VERCEL")
    _default_db = f"/tmp/story_creator{_env_suffix}.db" if _is_vercel else f"story_creator{_env_suffix}.db"
    default_db_path = os.environ.get("STORY_DB_PATH", _default_db)
    parser.add_argument(
        "--db-path",
        default=default_db_path,
        help="Đường dẫn đến database (chỉ dùng cho NoSQL). Tự động theo APP_ENV."
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
        mongo_db_name = f"story_creator{_env_suffix}" if _env_suffix else "story_creator_dev"
        api = APIBackend(
            data_dir=args.data_dir,
            storage_type=args.storage,
            db_path=args.db_path,
            mongo_db_name=mongo_db_name
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
