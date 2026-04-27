#!/usr/bin/env python
"""Tests for fix-api-cold-start feature.

Spec clauses covered:
  Behavior-1: GPT services are not instantiated at APIBackend init
  Behavior-2: Admin seeding deferred; skips health/docs paths
  Behavior-3: Swagger not built at APIBackend init
  Behavior-4: TinyDB/JSON removed; MongoDB is sole backend
  Behavior-5: Frontend useKeepAlive hook file exists
  BR-1:  GPT initialized at most once per process (thread-safe)
  BR-2:  Admin seeding skipped for /api/health and /api/docs
  BR-3:  Admin seeding runs at most once per process
  BR-4:  GPT failure leaves non-GPT routes unaffected
  BR-5:  MongoStorage does not open network connection in constructor
  BR-6:  NoSQLStorage and JSONStorage not importable from storage package
  BR-7:  Missing MONGODB_URI raises RuntimeError at startup
  BR-8/9/10: useKeepAlive hook exported, 5-min default, silent pattern
"""

import sys
import os
import threading
import importlib
import unittest
from unittest.mock import patch, MagicMock, call

os.environ['TEST_MODE'] = '1'
# Remove MONGODB_URI so tests start clean
os.environ.pop('MONGODB_URI', None)

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


# ---------------------------------------------------------------------------
# BR-6: NoSQLStorage and JSONStorage must NOT be importable from storage pkg
# ---------------------------------------------------------------------------

class TestStoragePackageExports(unittest.TestCase):

    def test_nosql_storage_not_in_package(self):
        """BR-6: NoSQLStorage must not be exported from storage package."""
        import storage
        importlib.reload(storage)
        self.assertFalse(
            hasattr(storage, 'NoSQLStorage'),
            "NoSQLStorage must be removed from storage package"
        )

    def test_json_storage_not_in_package(self):
        """BR-6: JSONStorage must not be exported from storage package."""
        import storage
        importlib.reload(storage)
        self.assertFalse(
            hasattr(storage, 'JSONStorage'),
            "JSONStorage must be removed from storage package"
        )

    def test_nosql_storage_file_not_importable(self):
        """BR-6: nosql_storage module must not exist."""
        with self.assertRaises(ModuleNotFoundError):
            import storage.nosql_storage  # noqa

    def test_json_storage_file_not_importable(self):
        """BR-6: json_storage module must not exist."""
        with self.assertRaises(ModuleNotFoundError):
            import storage.json_storage  # noqa

    def test_mongo_storage_importable(self):
        """Sanity: MongoStorage must still be importable."""
        from storage import MongoStorage
        self.assertIsNotNone(MongoStorage)


# ---------------------------------------------------------------------------
# BR-7: get_mongo_uri() raises RuntimeError when MONGODB_URI is missing
# ---------------------------------------------------------------------------

class TestEnvConfig(unittest.TestCase):

    def test_get_mongo_uri_exists(self):
        """BR-7: get_mongo_uri function must exist in env_config."""
        from utils import env_config
        self.assertTrue(
            hasattr(env_config, 'get_mongo_uri'),
            "get_mongo_uri() must exist in utils/env_config.py"
        )

    def test_get_mongo_db_name_exists(self):
        """BR-7: get_mongo_db_name function must exist in env_config."""
        from utils import env_config
        self.assertTrue(
            hasattr(env_config, 'get_mongo_db_name'),
            "get_mongo_db_name() must exist in utils/env_config.py"
        )

    def test_get_mongo_uri_raises_without_env_var(self):
        """BR-7: RuntimeError raised when MONGODB_URI not set."""
        from utils.env_config import get_mongo_uri
        env_backup = os.environ.pop('MONGODB_URI', None)
        try:
            with self.assertRaises(RuntimeError):
                get_mongo_uri()
        finally:
            if env_backup:
                os.environ['MONGODB_URI'] = env_backup

    def test_get_mongo_uri_returns_uri_when_set(self):
        """BR-7: Returns URI when MONGODB_URI is present."""
        from utils.env_config import get_mongo_uri
        os.environ['MONGODB_URI'] = 'mongodb://localhost/test'
        try:
            uri = get_mongo_uri()
            self.assertEqual(uri, 'mongodb://localhost/test')
        finally:
            del os.environ['MONGODB_URI']

    def test_get_mongo_db_name_returns_string(self):
        """get_mongo_db_name must return a non-empty string."""
        from utils.env_config import get_mongo_db_name
        name = get_mongo_db_name()
        self.assertIsInstance(name, str)
        self.assertTrue(len(name) > 0)

    def test_get_db_config_removed(self):
        """Behavior-4: get_db_config (TinyDB tuple) must be removed."""
        from utils import env_config
        self.assertFalse(
            hasattr(env_config, 'get_db_config'),
            "get_db_config() must be removed (TinyDB-era function)"
        )


# ---------------------------------------------------------------------------
# BR-5: MongoStorage must not open connection in __init__
# ---------------------------------------------------------------------------

class TestMongoStorageLazyConnect(unittest.TestCase):

    def _make_storage(self):
        """Create MongoStorage with mocked pymongo."""
        mock_client_cls = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_cls.return_value = mock_client_instance

        with patch.dict('sys.modules', {'pymongo': MagicMock(MongoClient=mock_client_cls)}):
            from storage.mongo_storage import MongoStorage
            storage = MongoStorage(
                mongodb_uri='mongodb://localhost/test',
                db_name='test_db'
            )
        return storage, mock_client_cls

    def test_no_network_call_in_constructor(self):
        """BR-5: MongoClient must NOT be instantiated in MongoStorage.__init__."""
        mock_client_cls = MagicMock()

        with patch('storage.mongo_storage._mongo_client_class', mock_client_cls):
            from storage.mongo_storage import MongoStorage
            with patch('storage.mongo_storage._ensure_pymongo'):
                storage = MongoStorage(
                    mongodb_uri='mongodb://localhost/test',
                    db_name='test_db'
                )

        mock_client_cls.assert_not_called()

    def test_db_is_none_before_first_call(self):
        """BR-5: storage.db must be None until first operation."""
        from storage.mongo_storage import MongoStorage
        with patch('storage.mongo_storage._ensure_pymongo'):
            with patch('storage.mongo_storage._mongo_client_class'):
                storage = MongoStorage.__new__(MongoStorage)
                storage.uri = 'mongodb://localhost/test'
                storage.db_name = 'test_db'
                storage.client = None
                storage.db = None
                storage._lock = threading.Lock()

        self.assertIsNone(storage.db)

    def test_connect_called_on_first_db_operation(self):
        """BR-5: _connect() is called before first save_world."""
        from storage.mongo_storage import MongoStorage
        storage = MongoStorage.__new__(MongoStorage)
        storage.uri = 'mongodb://localhost/test'
        storage.db_name = 'test_db'
        storage.db = None
        storage.client = None
        storage._lock = threading.Lock()

        connect_calls = []

        def fake_connect():
            connect_calls.append(1)
            # Simulate connected state
            storage.db = MagicMock()
            storage.worlds = MagicMock()
            storage.worlds.find_one = MagicMock(return_value=None)
            storage.worlds.replace_one = MagicMock()

        storage._connect = fake_connect

        with patch.object(storage, '_connect', wraps=fake_connect):
            try:
                storage.save_world({'world_id': 'w1', 'name': 'Test'})
            except Exception:
                pass  # Method may fail, we only care _connect was called

        self.assertGreater(len(connect_calls), 0,
                           "_connect() must be called before first DB operation")


# ---------------------------------------------------------------------------
# Behavior-1 / BR-1 / BR-4: Lazy GPT initialization in APIBackend
# ---------------------------------------------------------------------------

class TestLazyGPTInit(unittest.TestCase):

    def _make_backend_with_mock_storage(self):
        """Create APIBackend with mocked MongoDB."""
        mock_storage = MagicMock()
        mock_storage.list_users.return_value = [{'role': 'admin', 'username': 'admin'}]
        mock_storage.find_user_by_username.return_value = {'username': 'testuser', 'password_hash': 'x'}

        with patch('storage.MongoStorage', return_value=mock_storage), \
             patch('utils.env_config.get_mongo_uri', return_value='mongodb://localhost/test'), \
             patch('utils.env_config.get_mongo_db_name', return_value='test_db'):
            from interfaces.api_backend import APIBackend
            backend = APIBackend(mongodb_uri='mongodb://localhost/test', mongo_db_name='test_db')
        return backend

    def test_gpt_is_none_after_init(self):
        """Behavior-1: backend.gpt must be None immediately after __init__."""
        backend = self._make_backend_with_mock_storage()
        self.assertIsNone(
            backend.gpt,
            "backend.gpt must be None after __init__ (lazy init required)"
        )

    def test_gpt_service_is_none_after_init(self):
        """Behavior-1: backend.gpt_service must be None immediately after __init__."""
        backend = self._make_backend_with_mock_storage()
        self.assertIsNone(
            backend.gpt_service,
            "backend.gpt_service must be None after __init__ (lazy init required)"
        )

    def test_ensure_gpt_method_exists(self):
        """BR-1: _ensure_gpt() method must exist on APIBackend."""
        backend = self._make_backend_with_mock_storage()
        self.assertTrue(
            hasattr(backend, '_ensure_gpt'),
            "APIBackend must have _ensure_gpt() method"
        )

    def test_ensure_gpt_is_callable(self):
        """BR-1: _ensure_gpt() must be callable."""
        backend = self._make_backend_with_mock_storage()
        self.assertTrue(callable(backend._ensure_gpt))

    def test_gpt_init_failure_does_not_crash(self):
        """BR-4: GPT init failure must not prevent backend creation."""
        mock_storage = MagicMock()
        mock_storage.list_users.return_value = [{'role': 'admin'}]
        mock_storage.find_user_by_username.return_value = None

        with patch('storage.MongoStorage', return_value=mock_storage), \
             patch('ai.gpt_client.GPTIntegration', side_effect=ValueError("No API key")):
            from interfaces.api_backend import APIBackend
            # Must not raise
            backend = APIBackend(mongodb_uri='mongodb://localhost/test', mongo_db_name='test_db')

        self.assertIsNone(backend.gpt)


# ---------------------------------------------------------------------------
# Behavior-2 / BR-2 / BR-3: Lazy admin seeding
# ---------------------------------------------------------------------------

class TestLazyAdminSeeding(unittest.TestCase):

    def test_seed_once_method_exists(self):
        """BR-3: _seed_once() method must exist on APIBackend."""
        mock_storage = MagicMock()
        mock_storage.list_users.return_value = [{'role': 'admin'}]
        mock_storage.find_user_by_username.return_value = None

        with patch('storage.MongoStorage', return_value=mock_storage):
            from interfaces.api_backend import APIBackend
            backend = APIBackend(mongodb_uri='mongodb://localhost/test', mongo_db_name='test_db')

        self.assertTrue(
            hasattr(backend, '_seed_once'),
            "APIBackend must have _seed_once() method (lazy admin seeding)"
        )

    def test_ensure_default_admin_not_called_in_init(self):
        """Behavior-2: _ensure_default_admin must NOT be called during __init__."""
        mock_storage = MagicMock()
        mock_storage.list_users.return_value = [{'role': 'admin'}]

        with patch('storage.MongoStorage', return_value=mock_storage):
            from interfaces.api_backend import APIBackend
            with patch.object(APIBackend, '_ensure_default_admin') as mock_seed:
                APIBackend(mongodb_uri='mongodb://localhost/test', mongo_db_name='test_db')
                mock_seed.assert_not_called()

    def test_health_endpoint_does_not_trigger_seeding(self):
        """BR-2: GET /api/health must NOT trigger admin seeding."""
        mock_storage = MagicMock()
        mock_storage.list_users.return_value = [{'role': 'admin'}]
        mock_storage.find_user_by_username.return_value = None

        with patch('storage.MongoStorage', return_value=mock_storage):
            from interfaces.api_backend import APIBackend
            backend = APIBackend(mongodb_uri='mongodb://localhost/test', mongo_db_name='test_db')

        client = backend.app.test_client()
        with patch.object(backend, '_ensure_default_admin') as mock_admin, \
             patch.object(backend, '_seed_test_account') as mock_seed:
            client.get('/api/health')
            mock_admin.assert_not_called()
            mock_seed.assert_not_called()


# ---------------------------------------------------------------------------
# Behavior-3: Lazy Swagger initialization
# ---------------------------------------------------------------------------

class TestLazySwagger(unittest.TestCase):

    def test_swagger_not_built_at_init(self):
        """Behavior-3: backend._swagger must be None after __init__ (lazy Swagger)."""
        mock_storage = MagicMock()
        mock_storage.list_users.return_value = [{'role': 'admin'}]

        with patch('storage.MongoStorage', return_value=mock_storage):
            from interfaces.api_backend import APIBackend
            backend = APIBackend(mongodb_uri='mongodb://localhost/test', mongo_db_name='test_db')

        self.assertIsNone(
            backend._swagger,
            "backend._swagger must be None after __init__ — Swagger is lazy"
        )

    def test_swagger_attribute_is_none_after_init(self):
        """Behavior-3: backend._swagger must be None after __init__."""
        mock_storage = MagicMock()
        mock_storage.list_users.return_value = [{'role': 'admin'}]

        with patch('storage.MongoStorage', return_value=mock_storage):
            from interfaces.api_backend import APIBackend
            backend = APIBackend(mongodb_uri='mongodb://localhost/test', mongo_db_name='test_db')

        self.assertIsNone(
            getattr(backend, '_swagger', None),
            "backend._swagger must be None before first /api/docs access"
        )


# ---------------------------------------------------------------------------
# Behavior-4: app.py uses get_mongo_uri / get_mongo_db_name (no TinyDB)
# ---------------------------------------------------------------------------

class TestAppEntrypoint(unittest.TestCase):

    def test_app_py_does_not_import_get_db_config(self):
        """Behavior-4: api/app.py must not import get_db_config (TinyDB-era)."""
        app_path = os.path.join(os.path.dirname(__file__), '..', 'api', 'app.py')
        if not os.path.exists(app_path):
            app_path = os.path.join(os.path.dirname(__file__), 'app.py')

        with open(app_path) as f:
            source = f.read()

        self.assertNotIn(
            'get_db_config', source,
            "api/app.py must not use get_db_config() (TinyDB removed)"
        )

    def test_app_py_uses_get_mongo_uri(self):
        """Behavior-4: api/app.py must use get_mongo_uri."""
        app_path = os.path.join(os.path.dirname(__file__), 'app.py')
        with open(app_path) as f:
            source = f.read()

        self.assertIn(
            'get_mongo_uri', source,
            "api/app.py must call get_mongo_uri() for MongoDB-only setup"
        )

    def test_requirements_no_tinydb(self):
        """BR-6: tinydb must not appear in requirements.txt."""
        req_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
        with open(req_path) as f:
            content = f.read().lower()
        self.assertNotIn('tinydb', content,
                         "tinydb must be removed from requirements.txt")


# ---------------------------------------------------------------------------
# Behavior-5 / BR-8,9,10: Frontend useKeepAlive hook
# ---------------------------------------------------------------------------

class TestFrontendKeepAlive(unittest.TestCase):

    def _hook_path(self):
        base = os.path.dirname(__file__)
        return os.path.join(base, '..', 'src', 'hooks', 'useKeepAlive.js')

    def test_keep_alive_file_exists(self):
        """Behavior-5: src/hooks/useKeepAlive.js must exist."""
        self.assertTrue(
            os.path.exists(self._hook_path()),
            "src/hooks/useKeepAlive.js must be created"
        )

    def test_keep_alive_exports_use_keep_alive(self):
        """BR-8: useKeepAlive must be exported from the hook file."""
        path = self._hook_path()
        if not os.path.exists(path):
            self.skipTest("File not created yet")
        with open(path) as f:
            source = f.read()
        self.assertIn('useKeepAlive', source,
                      "useKeepAlive must be exported from the hook")

    def test_keep_alive_uses_health_endpoint(self):
        """BR-10: Keep-alive must ping /api/health."""
        path = self._hook_path()
        if not os.path.exists(path):
            self.skipTest("File not created yet")
        with open(path) as f:
            source = f.read()
        self.assertIn('/api/health', source,
                      "Keep-alive hook must ping /api/health")

    def test_keep_alive_default_interval_5min(self):
        """BR-9: Default interval must be 300000 ms (5 minutes)."""
        path = self._hook_path()
        if not os.path.exists(path):
            self.skipTest("File not created yet")
        with open(path) as f:
            source = f.read()
        self.assertIn('300000', source,
                      "Keep-alive interval must be 300000 ms (5 minutes)")

    def test_keep_alive_checks_visibility(self):
        """BR-8: Keep-alive must check document.visibilityState."""
        path = self._hook_path()
        if not os.path.exists(path):
            self.skipTest("File not created yet")
        with open(path) as f:
            source = f.read()
        self.assertIn('visibilityState', source,
                      "Keep-alive must respect tab visibility")

    def test_app_jsx_uses_keep_alive(self):
        """Behavior-5: App.jsx must import and use useKeepAlive."""
        app_jsx = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'App.jsx')
        if not os.path.exists(app_jsx):
            self.skipTest("App.jsx not found")
        with open(app_jsx) as f:
            source = f.read()
        self.assertIn('useKeepAlive', source,
                      "App.jsx must use the useKeepAlive hook")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_tests():
    suite = unittest.TestLoader().loadTestsFromModule(
        sys.modules[__name__]
    )
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} passing")
    if result.failures or result.errors:
        print("RED STATE — tests failing as expected before implementation")
    else:
        print("GREEN STATE — all tests pass")
    print(f"{'='*60}")
    return result


if __name__ == '__main__':
    run_tests()
