"""Pure API backend for Story Creator - No template rendering, API-only."""

from flask import Flask, request
from flask_cors import CORS
from generators import WorldGenerator, StoryGenerator, StoryLinker
from storage import MongoStorage
from ai.gpt_client import GPTIntegration
from services import GPTService, AuthService
from services import EventService
from services.task_store import TaskStore
from services.activity_log_service import init_activity_log_service
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
import logging
import os
import re
import signal
import threading
import psutil
import time

logger = logging.getLogger(__name__)

# Module-level lazy-init sentinels
_gpt_initialized = False
_gpt_lock = threading.Lock()
_admin_seeded = False


class APIBackend:
    """Pure REST API backend for Story Creator."""

    def __init__(
        self,
        mongodb_uri: str,
        mongo_db_name: str = "story_creator_dev"
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
        # Add Vercel production URL only if it matches the expected shape.
        # Without this check, a tampered / typo'd VERCEL_URL would land in the
        # CORS allowlist unchallenged.
        vercel_url = os.environ.get("VERCEL_URL")
        if vercel_url:
            if re.match(r'^[a-zA-Z0-9.-]+\.vercel\.app$', vercel_url):
                allowed_origins.append(f"https://{vercel_url}")
            else:
                logger.warning(
                    "VERCEL_URL %r does not match expected pattern — "
                    "skipping CORS entry",
                    vercel_url,
                )
        CORS(self.app, resources={
            r"/api/*": {
                "origins": allowed_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })

        # Store Swagger config — will be initialized lazily on first /api/docs request
        self._swagger_config = {
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

        self._swagger_template = {
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

        self._swagger = None

        # Register global error handlers
        from interfaces.error_handlers import register_error_handlers
        register_error_handlers(self.app)

        # Register request/response logging middleware
        from interfaces.logging_middleware import register_logging_middleware
        register_logging_middleware(self.app)

        # Initialize rate limiter (no-op if flask-limiter not installed)
        from interfaces.rate_limiter import create_limiter
        self.limiter = create_limiter(self.app)

        # Initialize storage (MongoDB only — lazy connect, no network I/O here)
        self.storage = MongoStorage(mongodb_uri, db_name=mongo_db_name)
        self.storage_label = "MongoDB Atlas"

        # Initialize generators
        self.world_generator = WorldGenerator()
        self.story_generator = StoryGenerator()
        self.story_linker = StoryLinker()
        self.diagram_generator = RelationshipDiagram(canvas_width=1200, canvas_height=800)

        # GPT integration — deferred until first GPT request (_ensure_gpt)
        self.gpt = None
        self.gpt_service = None
        self.event_service = EventService(None, self.storage)
        self.has_gpt = False

        # Initialize Auth service
        self.auth_service = AuthService(self.storage)

        # Initialize auth middleware
        init_auth_middleware(self.auth_service)

        # Store for async GPT results (persisted in database)
        self.gpt_results = TaskStore(self.storage)

        # Activity log service (in-memory mock, singleton per process)
        self.activity_log_service = init_activity_log_service()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Register API routes using blueprints
        self._register_blueprints()

        # Register before_request hooks for lazy init
        backend = self

        @self.app.after_request
        def _add_security_headers(response):
            """Set defensive HTTP headers on every response.

            Uses ``setdefault`` so a route that already set a specific
            header (e.g. a bespoke Content-Security-Policy) is not
            clobbered. HSTS is only emitted when the request was served
            over HTTPS (directly or via a proxy) to avoid broadcasting
            it over plain HTTP in local dev.
            """
            response.headers.setdefault('X-Content-Type-Options', 'nosniff')
            response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
            response.headers.setdefault(
                'Referrer-Policy', 'strict-origin-when-cross-origin'
            )
            is_https = request.is_secure or (
                request.headers.get('X-Forwarded-Proto', '').lower() == 'https'
            )
            if is_https:
                response.headers.setdefault(
                    'Strict-Transport-Security',
                    'max-age=31536000; includeSubDomains',
                )
            return response

        @self.app.before_request
        def _lazy_init():
            path = request.path
            # Always initialize Swagger when docs are requested
            if path.startswith('/api/docs') or path.startswith('/flasgger') or path.startswith('/apispec'):
                backend._ensure_swagger()
                return
            # Skip admin seeding for health checks
            if path.startswith('/api/health'):
                return
            backend._seed_once()

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
        Ensure a default admin account exists, gated on INITIAL_ADMIN_PASSWORD.

        - If an admin already exists: no-op (unchanged behavior on prod).
        - If no admin AND INITIAL_ADMIN_PASSWORD is unset: log a warning and
          skip — operators must set the env var to seed the initial admin.
        - If no admin AND INITIAL_ADMIN_PASSWORD is set: create an admin
          with that password. The password is never logged or printed.
        """
        all_users = self.storage.list_users()
        admin_users = [u for u in all_users if u.get('role') == 'admin']

        if admin_users:
            logger.info(
                "Found %d admin account(s); skipping seed", len(admin_users)
            )
            return

        initial_pwd = os.environ.get('INITIAL_ADMIN_PASSWORD')
        if not initial_pwd:
            logger.warning(
                "No admin account exists and INITIAL_ADMIN_PASSWORD is unset — "
                "skipping admin seed. Set INITIAL_ADMIN_PASSWORD to auto-create "
                "the initial admin."
            )
            return

        from core.models import User
        password_hash = self.auth_service.hash_password(initial_pwd)
        admin_user = User(
            username="admin",
            email="admin@storycreator.com",
            password_hash=password_hash,
            role="admin",
        )
        self.storage.save_user(admin_user.to_dict())
        logger.info("Admin account seeded from INITIAL_ADMIN_PASSWORD env")

    def _seed_test_account(self):
        """Seed a hard-coded test account for local / nonprod development.

        Caller (_seed_once) gates this behind both VERCEL_ENV != 'production'
        AND SEED_TEST_USER == '1'. The password is never printed or logged.
        """
        from core.models import User

        test_password = "Test@123"
        existing = self.storage.find_user_by_username("testuser")

        if existing:
            if not self.auth_service.verify_password(
                test_password, existing.get('password_hash', '')
            ):
                existing['password_hash'] = self.auth_service.hash_password(
                    test_password
                )
                self.storage.save_user(existing)
                logger.info("Test account password reset (nonprod)")
            return

        password_hash = self.auth_service.hash_password(test_password)
        test_user = User(
            username="testuser",
            email="test@storycreator.local",
            password_hash=password_hash,
            role="user",
        )
        self.storage.save_user(test_user.to_dict())
        logger.info("Test account seeded (nonprod)")

    def _ensure_gpt(self):
        """Lazily initialize GPT integration on first use. Thread-safe, runs once."""
        global _gpt_initialized, _gpt_lock
        if _gpt_initialized:
            return
        with _gpt_lock:
            if _gpt_initialized:
                return
            try:
                self.gpt = GPTIntegration()
                self.gpt_service = GPTService(self.gpt)
                self.event_service = EventService(self.gpt, self.storage)
                self.has_gpt = True
                print("✅ GPT initialized on first use")
            except (ImportError, ValueError) as e:
                self.has_gpt = False
                print(f"⚠️  GPT not available: {e}")
            _gpt_initialized = True

    def _seed_once(self):
        """Run admin + test seeding exactly once per process.

        Test account requires explicit opt-in via SEED_TEST_USER=1 so that
        the hardcoded Test@123 user is never created by default — not on
        Vercel preview deployments, not in CI, not in local shells where
        the flag was never set.
        """
        global _admin_seeded
        if _admin_seeded:
            return
        _admin_seeded = True
        self._ensure_default_admin()
        if (
            os.environ.get("VERCEL_ENV") != "production"
            and os.environ.get("SEED_TEST_USER") == "1"
        ):
            self._seed_test_account()

    def _ensure_swagger(self):
        """Initialize Flasgger on first /api/docs request."""
        if self._swagger is None:
            from flasgger import Swagger
            self._swagger = Swagger(self.app, config=self._swagger_config, template=self._swagger_template)

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
            backend=self,
            gpt_results=self.gpt_results,
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
            gpt_results=self.gpt_results,
            backend=self
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
            auth_service=self.auth_service,
            activity_log_service=self.activity_log_service,
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
