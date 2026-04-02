"""Pure API backend for Story Creator - No template rendering, API-only."""

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from generators import WorldGenerator, StoryGenerator, StoryLinker
from storage import NoSQLStorage, JSONStorage, MongoStorage
from ai.gpt_client import GPTIntegration
from services import GPTService, AuthService
from services import EventService
from services.task_store import TaskStore
from visualization import RelationshipDiagram
from interfaces.auth_middleware import init_auth_middleware
from interfaces.routes import (
    create_health_bp,
    create_world_bp,
    create_story_bp,
    create_gpt_bp,
    create_stats_bp,
    create_event_bp,
    create_auth_bp,
    create_admin_bp,
    create_collaborator_bp,
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

        # Enable CORS for React frontend (local dev + Vercel production)
        allowed_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        # Add Vercel production URL if set
        vercel_url = os.environ.get("VERCEL_URL")
        if vercel_url:
            allowed_origins.append(f"https://{vercel_url}")
        CORS(self.app, resources={
            r"/api/*": {
                "origins": allowed_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
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
                {"name": "Authentication", "description": "User authentication and authorization"},
                {"name": "Worlds", "description": "World management"},
                {"name": "Stories", "description": "Story management"},
                {"name": "Events", "description": "Event timeline management"},
                {"name": "GPT", "description": "GPT integration"},
                {"name": "Stats", "description": "Statistics"},
            ]
        }

        self.swagger = Swagger(self.app, config=swagger_config, template=swagger_template)

        # Register global error handlers
        from interfaces.error_handlers import register_error_handlers
        register_error_handlers(self.app)

        # Register request/response logging middleware
        from interfaces.logging_middleware import register_logging_middleware
        register_logging_middleware(self.app)

        # Initialize rate limiter (no-op if flask-limiter not installed)
        from interfaces.rate_limiter import create_limiter
        self.limiter = create_limiter(self.app)

        # Initialize storage
        # Priority: MongoDB (if MONGODB_URI set) → NoSQL (TinyDB) → JSON files
        mongodb_uri = os.environ.get('MONGODB_URI')
        if mongodb_uri and MongoStorage:
            try:
                self.storage = MongoStorage(mongodb_uri)
                self.storage_label = "MongoDB Atlas"
                print("✅ Using MongoDB Atlas for persistent storage")
            except Exception as e:
                print(f"⚠️  MongoDB connection failed: {e}")
                print("   Falling back to TinyDB...")
                self.storage = NoSQLStorage(db_path)
                self.storage_label = "NoSQL Database (fallback)"
        elif storage_type == "nosql":
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
            self.event_service = EventService(self.gpt, self.storage)
            self.has_gpt = True
        except (ImportError, ValueError) as e:
            self.gpt = None
            self.gpt_service = None
            self.event_service = EventService(None, self.storage)
            self.has_gpt = False
            print(f"⚠️  GPT not available: {e}")

        # Initialize Auth service
        self.auth_service = AuthService(self.storage)

        # Initialize auth middleware
        init_auth_middleware(self.auth_service)

        # Ensure default admin account exists
        self._ensure_default_admin()

        # Seed test account in nonprod (no VERCEL env var)
        if not os.environ.get("VERCEL"):
            self._seed_test_account()

        # Store for async GPT results (persisted in database)
        self.gpt_results = TaskStore(self.storage)

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

    def _ensure_default_admin(self):
        """
        Ensure a default admin account exists in the database.
        This admin account will be created automatically if no admin exists,
        even after database truncation.

        Default credentials:
        - Username: admin
        - Email: admin@storycreator.com
        - Password: Admin@123
        - Role: admin
        """
        # Check if any admin user exists
        all_users = self.storage.list_users()
        admin_users = [u for u in all_users if u.get('role') == 'admin']

        if not admin_users:
            # No admin found, create default admin
            from core.models import User

            admin_password = "Admin@123"
            password_hash = self.auth_service.hash_password(admin_password)

            admin_user = User(
                username="admin",
                email="admin@storycreator.com",
                password_hash=password_hash,
                role="admin"
            )

            # Save admin to database
            self.storage.save_user(admin_user.to_dict())

            print("🔐 Tạo tài khoản admin mặc định:")
            print("   Username: admin")
            print("   Email: admin@storycreator.com")
            print("   Password: Admin@123")
            print("   ⚠️  VUI LÒNG ĐỔI MẬT KHẨU SAU KHI ĐĂNG NHẬP!")
        else:
            # Admin exists
            admin_count = len(admin_users)
            print(f"✅ Đã tìm thấy {admin_count} tài khoản admin trong hệ thống")

    def _seed_test_account(self):
        """Seed a hard-coded test account for local / nonprod development.

        Credentials:
        - Username: testuser
        - Email:    test@storycreator.local
        - Password: Test@123
        - Role:     user
        """
        from core.models import User

        if self.storage.find_user_by_username("testuser"):
            return  # already seeded

        password_hash = self.auth_service.hash_password("Test@123")
        test_user = User(
            username="testuser",
            email="test@storycreator.local",
            password_hash=password_hash,
            role="user"
        )
        self.storage.save_user(test_user.to_dict())
        print("🧪 Test account seeded (nonprod only):")
        print("   Username: testuser")
        print("   Password: Test@123")

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
            has_gpt=self.has_gpt,
            storage=self.storage,
            flush_data=self._flush_data,
            limiter=self.limiter
        )
        self.app.register_blueprint(gpt_bp)

        # Stats routes
        stats_bp = create_stats_bp(
            storage=self.storage,
            has_gpt=self.has_gpt
        )
        self.app.register_blueprint(stats_bp)

        # Event routes
        event_bp = create_event_bp(
            storage=self.storage,
            event_service=self.event_service,
            gpt_results=self.gpt_results,
            has_gpt=self.has_gpt
        )
        self.app.register_blueprint(event_bp)

        # Auth routes
        auth_bp = create_auth_bp(
            storage=self.storage,
            auth_service=self.auth_service,
            limiter=self.limiter
        )
        self.app.register_blueprint(auth_bp)

        # Admin routes
        admin_bp = create_admin_bp(
            storage=self.storage,
            auth_service=self.auth_service
        )
        self.app.register_blueprint(admin_bp)

        collaborator_bp = create_collaborator_bp(
            storage=self.storage,
            flush_data=self._flush_data
        )
        self.app.register_blueprint(collaborator_bp)

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
