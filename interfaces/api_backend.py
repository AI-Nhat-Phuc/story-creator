"""Pure API backend for Story Creator - No template rendering, API-only."""

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from generators import WorldGenerator, StoryGenerator, StoryLinker
from storage import NoSQLStorage, JSONStorage
from ai.gpt_client import GPTIntegration
from services import GPTService
from visualization import RelationshipDiagram
from interfaces.routes import (
    create_health_bp,
    create_world_bp,
    create_story_bp,
    create_gpt_bp,
    create_stats_bp
)
import os
import signal
import psutil
import time


class APIBackend:
    """Pure REST API backend for Story Creator."""

    def __init__(
        self,
        data_dir: str = "data",
        storage_type: str = "nosql",
        db_path: str = "story_creator.db"
    ):
        """Initialize API Backend."""
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)

        # Enable CORS for React frontend
        CORS(self.app, resources={
            r"/api/*": {
                "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type"]
            }
        })

        # Initialize Swagger UI
        swagger_config = {
            "headers": [],
            "specs": [
                {
                    "endpoint": 'apispec',
                    "route": '/apispec.json',
                    "rule_filter": lambda rule: True,
                    "model_filter": lambda tag: True,
                }
            ],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/api/docs"
        }

        swagger_template = {
            "swagger": "2.0",
            "info": {
                "title": "Story Creator API",
                "description": "REST API for Story Creator - Interactive storytelling system with worlds, stories, characters, and locations",
                "version": "1.0.0",
                "contact": {
                    "name": "Story Creator Team",
                    "url": "https://github.com/AI-Nhat-Phuc/story-creator"
                }
            },
            "host": "localhost:5000",
            "basePath": "/",
            "schemes": ["http"],
            "tags": [
                {"name": "Health", "description": "Health check endpoints"},
                {"name": "Worlds", "description": "World management"},
                {"name": "Stories", "description": "Story management"},
                {"name": "GPT", "description": "GPT integration"},
                {"name": "Stats", "description": "Statistics"}
            ]
        }

        self.swagger = Swagger(self.app, config=swagger_config, template=swagger_template)

        # Initialize storage
        if storage_type == "nosql":
            self.storage = NoSQLStorage(db_path)
            self.storage_label = "NoSQL Database"
        else:
            self.storage = JSONStorage(data_dir)
            self.storage_label = "JSON Files"

        # Initialize generators
        self.world_generator = WorldGenerator()
        self.story_generator = StoryGenerator()
        self.story_linker = StoryLinker()
        self.diagram_generator = RelationshipDiagram(canvas_width=1200, canvas_height=800)

        # Initialize GPT integration (optional)
        try:
            self.gpt = GPTIntegration()
            self.gpt_service = GPTService(self.gpt)
            self.has_gpt = True
        except (ImportError, ValueError) as e:
            self.gpt = None
            self.gpt_service = None
            self.has_gpt = False
            print(f"⚠️  GPT not available: {e}")

        # Store for async GPT results
        self.gpt_results = {}

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Register API routes using blueprints
        self._register_blueprints()

    def _signal_handler(self, signum, frame):
        """Handle graceful shutdown."""
        print("\n🔄 Shutting down gracefully...")
        self._flush_data()
        self.storage.close()
        exit(0)

    def _flush_data(self):
        """Flush data to disk."""
        if hasattr(self.storage, 'flush'):
            self.storage.flush()

    def _register_blueprints(self):
        """Register all API route blueprints."""
        # Health routes
        health_bp = create_health_bp(
            storage_label=self.storage_label,
            has_gpt=self.has_gpt
        )
        self.app.register_blueprint(health_bp)

        # World routes
        world_bp = create_world_bp(
            storage=self.storage,
            world_generator=self.world_generator,
            diagram_generator=self.diagram_generator,
            flush_data=self._flush_data
        )
        self.app.register_blueprint(world_bp)

        # Story routes
        story_bp = create_story_bp(
            storage=self.storage,
            story_generator=self.story_generator,
            flush_data=self._flush_data
        )
        self.app.register_blueprint(story_bp)

        # GPT routes
        gpt_bp = create_gpt_bp(
            gpt=self.gpt,
            gpt_service=self.gpt_service,
            gpt_results=self.gpt_results,
            has_gpt=self.has_gpt
        )
        self.app.register_blueprint(gpt_bp)

        # Stats routes
        stats_bp = create_stats_bp(
            storage=self.storage,
            has_gpt=self.has_gpt
        )
        self.app.register_blueprint(stats_bp)

    def _kill_existing_server(self, port=5000):
        """Kill any existing process using the specified port."""
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        try:
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result != 0:
                return False

            print(f"⚠️  Port {port} đang được sử dụng")
        except Exception:
            sock.close()
            return False

        # Find and kill the process
        killed = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Try to get connections - may not work on all platforms
                try:
                    connections = proc.connections()
                except (AttributeError, psutil.AccessDenied):
                    # connections() not available or access denied, skip this process
                    continue

                for conn in connections:
                    if hasattr(conn, 'laddr') and conn.laddr.port == port:
                        print(f"🛑 Đang tắt server cũ (PID: {proc.pid})...")
                        proc.terminate()
                        proc.wait(timeout=3)
                        killed = True
                        print(f"✅ Đã tắt server cũ")
                        time.sleep(0.5)
                        break
                if killed:
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue

        return killed

    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Run the Flask API server."""
        # STEP 1: Check if port is already in use BEFORE doing anything
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                # Port in use - try to kill existing server
                print(f"⚠️  Port {port} đang được sử dụng, đang cố gắng tắt server cũ...")
                try:
                    killed = self._kill_existing_server(port)
                    if killed:
                        # Wait a bit for port to be released
                        time.sleep(1)
                        # Check again
                        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock2.settimeout(1)
                        result2 = sock2.connect_ex((host, port))
                        sock2.close()
                        if result2 == 0:
                            # Still in use after killing
                            print(f"\n❌ LỖI: Port {port} vẫn đang được sử dụng sau khi tắt server cũ!")
                            print(f"Không thể khởi động server. Vui lòng:")
                            print(f"1. Chờ vài giây rồi thử lại")
                            print(f"2. Hoặc dùng port khác: --port <số_port>")
                            print(f"3. Hoặc chạy: netstat -ano | findstr :{port}")
                            exit(1)
                    else:
                        # Could not kill - port still in use
                        print(f"\n❌ LỖI: Port {port} đang được sử dụng bởi process khác!")
                        print(f"Không thể khởi động server. Vui lòng:")
                        print(f"1. Tắt server đang chạy")
                        print(f"2. Hoặc dùng port khác: --port <số_port>")
                        print(f"3. Hoặc chạy: netstat -ano | findstr :{port}")
                        exit(1)
                except Exception as e:
                    print(f"\n❌ LỖI: Không thể kiểm tra/tắt server cũ: {e}")
                    print(f"Port {port} có thể đang được sử dụng. Vui lòng kiểm tra thủ công.")
                    exit(1)
        except Exception:
            sock.close()

        if not debug:
            print(f"\n🚀 Story Creator API Backend", flush=True)
            print(f"📊 Storage: {self.storage_label}", flush=True)
            print(f"🤖 GPT: {'✅ Enabled' if self.has_gpt else '❌ Disabled'}", flush=True)
            print(f"\n🌐 API Server: http://{host}:{port}/api", flush=True)
            print(f"📖 Press Ctrl+C to stop\n", flush=True)

        self.app.run(host=host, port=port, debug=debug, use_reloader=False)
