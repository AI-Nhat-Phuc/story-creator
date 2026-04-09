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


def _resolve_mongodb_uri(mongo_db_name: str) -> str:
    """Return MONGODB_URI from env, falling back to mongomock for local dev.

    When MONGODB_URI is not set (local development), uses mongomock so the
    backend can start without a real MongoDB instance.  mongomock stores data
    in memory for the lifetime of the process — sufficient for e2e tests.
    """
    uri = os.environ.get('MONGODB_URI')
    if uri:
        return uri

    try:
        import mongomock  # noqa: F401 — just check it's importable
        mock_uri = f'mongomock://localhost/{mongo_db_name}'
        logging.getLogger(__name__).warning(
            'MONGODB_URI not set — using in-memory mongomock for local dev. '
            'Data will be lost when the process exits.'
        )
        return mock_uri
    except ImportError:
        raise RuntimeError(
            'MONGODB_URI is not set and mongomock is not installed.\n'
            'For local dev: pip install mongomock\n'
            'For production: set MONGODB_URI in your .env file.'
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

    if args.interface == "simulation":
        logger.info("Launching simulation mode")
        from interfaces.simulation_interface import main as sim_main
        sim_main()
    elif args.interface == "api":
        from utils.env_config import get_mongo_db_name
        mongo_db_name = get_mongo_db_name()
        mongodb_uri = _resolve_mongodb_uri(mongo_db_name)

        logger.info("Launching API Backend")
        from interfaces.api_backend import APIBackend
        api = APIBackend(mongodb_uri=mongodb_uri, mongo_db_name=mongo_db_name)
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
