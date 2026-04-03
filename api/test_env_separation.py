#!/usr/bin/env python
"""Tests for prod/nonprod environment data separation.

Covers every spec clause in .task/separate_prod_nonprod_data/task_spec.md
Expected: ALL FAIL before implementation (red state).
"""

import sys
import os

# Add api/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
os.environ['TEST_MODE'] = '1'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def set_env(**kwargs):
    """Temporarily set env vars, return original values."""
    originals = {}
    for k, v in kwargs.items():
        originals[k] = os.environ.get(k)
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    return originals


def restore_env(originals):
    for k, v in originals.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


# ---------------------------------------------------------------------------
# Test 1 — BR-1: APP_ENV=production → prod db names
# ---------------------------------------------------------------------------

def test_production_env_db_path():
    """BR-1: APP_ENV=production returns prod TinyDB path (non-Vercel)."""
    orig = set_env(APP_ENV='production', VERCEL=None, STORY_DB_PATH=None)
    try:
        # Import fresh each test via importlib to reset module state
        import importlib
        import utils.env_config as ec
        importlib.reload(ec)
        db_path, mongo_db_name = ec.get_db_config()
        assert 'prod' in db_path, f"Expected 'prod' in db_path, got: {db_path}"
        assert db_path.endswith('.db'), f"Expected .db extension, got: {db_path}"
        assert mongo_db_name == 'story_creator_prod', f"Expected 'story_creator_prod', got: {mongo_db_name}"
        print("  PASS: test_production_env_db_path")
    finally:
        restore_env(orig)


def test_production_env_vercel_db_path():
    """BR-1: APP_ENV=production on Vercel → /tmp prefix."""
    orig = set_env(APP_ENV='production', VERCEL='1', STORY_DB_PATH=None)
    try:
        import importlib
        import utils.env_config as ec
        importlib.reload(ec)
        db_path, mongo_db_name = ec.get_db_config()
        assert db_path.startswith('/tmp/'), f"Expected /tmp/ prefix on Vercel, got: {db_path}"
        assert 'prod' in db_path, f"Expected 'prod' in db_path, got: {db_path}"
        assert mongo_db_name == 'story_creator_prod'
        print("  PASS: test_production_env_vercel_db_path")
    finally:
        restore_env(orig)


# ---------------------------------------------------------------------------
# Test 2 — BR-2: APP_ENV=staging → staging db names
# ---------------------------------------------------------------------------

def test_staging_env_db_names():
    """BR-2: APP_ENV=staging returns staging db names."""
    orig = set_env(APP_ENV='staging', VERCEL=None, STORY_DB_PATH=None)
    try:
        import importlib
        import utils.env_config as ec
        importlib.reload(ec)
        db_path, mongo_db_name = ec.get_db_config()
        assert 'staging' in db_path, f"Expected 'staging' in db_path, got: {db_path}"
        assert mongo_db_name == 'story_creator_staging', f"Expected 'story_creator_staging', got: {mongo_db_name}"
        print("  PASS: test_staging_env_db_names")
    finally:
        restore_env(orig)


# ---------------------------------------------------------------------------
# Test 3 — BR-3: default (no APP_ENV) → dev db names
# ---------------------------------------------------------------------------

def test_default_env_db_names():
    """BR-3: No APP_ENV → development defaults, local path story_creator.db."""
    orig = set_env(APP_ENV=None, VERCEL=None, STORY_DB_PATH=None)
    try:
        import importlib
        import utils.env_config as ec
        importlib.reload(ec)
        db_path, mongo_db_name = ec.get_db_config()
        assert db_path == 'story_creator.db', f"Expected 'story_creator.db', got: {db_path}"
        assert mongo_db_name == 'story_creator_dev', f"Expected 'story_creator_dev', got: {mongo_db_name}"
        print("  PASS: test_default_env_db_names")
    finally:
        restore_env(orig)


def test_development_explicit_env_db_names():
    """BR-3: APP_ENV=development → same as default."""
    orig = set_env(APP_ENV='development', VERCEL=None, STORY_DB_PATH=None)
    try:
        import importlib
        import utils.env_config as ec
        importlib.reload(ec)
        db_path, mongo_db_name = ec.get_db_config()
        assert db_path == 'story_creator.db', f"Expected 'story_creator.db', got: {db_path}"
        assert mongo_db_name == 'story_creator_dev', f"Expected 'story_creator_dev', got: {mongo_db_name}"
        print("  PASS: test_development_explicit_env_db_names")
    finally:
        restore_env(orig)


# ---------------------------------------------------------------------------
# Test 4 — BR-4: STORY_DB_PATH overrides db_path
# ---------------------------------------------------------------------------

def test_story_db_path_override():
    """BR-4: STORY_DB_PATH env var overrides db_path regardless of APP_ENV."""
    orig = set_env(APP_ENV='production', VERCEL=None, STORY_DB_PATH='/custom/path.db')
    try:
        import importlib
        import utils.env_config as ec
        importlib.reload(ec)
        db_path, mongo_db_name = ec.get_db_config()
        assert db_path == '/custom/path.db', f"Expected STORY_DB_PATH override, got: {db_path}"
        # mongo_db_name still follows APP_ENV
        assert mongo_db_name == 'story_creator_prod', f"Expected 'story_creator_prod', got: {mongo_db_name}"
        print("  PASS: test_story_db_path_override")
    finally:
        restore_env(orig)


# ---------------------------------------------------------------------------
# Test 5 — Edge Cases: invalid APP_ENV → fallback to development
# ---------------------------------------------------------------------------

def test_invalid_app_env_fallback():
    """Edge Case: Invalid APP_ENV falls back to development defaults."""
    orig = set_env(APP_ENV='invalid_env_xyz', VERCEL=None, STORY_DB_PATH=None)
    try:
        import importlib
        import utils.env_config as ec
        importlib.reload(ec)
        db_path, mongo_db_name = ec.get_db_config()
        assert db_path == 'story_creator.db', f"Expected fallback to 'story_creator.db', got: {db_path}"
        assert mongo_db_name == 'story_creator_dev', f"Expected fallback to 'story_creator_dev', got: {mongo_db_name}"
        print("  PASS: test_invalid_app_env_fallback")
    finally:
        restore_env(orig)


# ---------------------------------------------------------------------------
# Test 6 — MongoStorage default db_name is not "story_creator" (old prod name)
# ---------------------------------------------------------------------------

def test_mongo_storage_default_db_name():
    """BR-1/BR-3: MongoStorage default db_name must be 'story_creator_dev', not 'story_creator'."""
    from storage.mongo_storage import MongoStorage
    import inspect
    sig = inspect.signature(MongoStorage.__init__)
    default_db_name = sig.parameters['db_name'].default
    assert default_db_name == 'story_creator_dev', (
        f"MongoStorage default db_name should be 'story_creator_dev', got: '{default_db_name}'. "
        "Old default 'story_creator' would mix prod/nonprod data."
    )
    print("  PASS: test_mongo_storage_default_db_name")


# ---------------------------------------------------------------------------
# Test 7 — APIBackend accepts mongo_db_name param
# ---------------------------------------------------------------------------

def test_api_backend_accepts_mongo_db_name():
    """BR-1: APIBackend.__init__ must accept mongo_db_name parameter."""
    from interfaces.api_backend import APIBackend
    import inspect
    sig = inspect.signature(APIBackend.__init__)
    assert 'mongo_db_name' in sig.parameters, (
        "APIBackend.__init__ must accept 'mongo_db_name' parameter"
    )
    print("  PASS: test_api_backend_accepts_mongo_db_name")


# ---------------------------------------------------------------------------
# Test 8 — Prod and nonprod use different db names (isolation guarantee)
# ---------------------------------------------------------------------------

def test_prod_nonprod_use_different_dbs():
    """Behavior: prod and nonprod must never share the same db path or name."""
    import importlib
    import utils.env_config as ec

    orig_prod = set_env(APP_ENV='production', VERCEL=None, STORY_DB_PATH=None)
    importlib.reload(ec)
    prod_path, prod_mongo = ec.get_db_config()
    restore_env(orig_prod)

    orig_dev = set_env(APP_ENV='development', VERCEL=None, STORY_DB_PATH=None)
    importlib.reload(ec)
    dev_path, dev_mongo = ec.get_db_config()
    restore_env(orig_dev)

    assert prod_path != dev_path, f"Prod and dev must use different db paths! Both: {prod_path}"
    assert prod_mongo != dev_mongo, f"Prod and dev must use different mongo db names! Both: {prod_mongo}"
    print("  PASS: test_prod_nonprod_use_different_dbs")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

TESTS = [
    test_production_env_db_path,
    test_production_env_vercel_db_path,
    test_staging_env_db_names,
    test_default_env_db_names,
    test_development_explicit_env_db_names,
    test_story_db_path_override,
    test_invalid_app_env_fallback,
    test_mongo_storage_default_db_name,
    test_api_backend_accepts_mongo_db_name,
    test_prod_nonprod_use_different_dbs,
]


if __name__ == '__main__':
    print(f"\n=== TEST: separate prod/nonprod data ({len(TESTS)} tests) ===\n")
    passed = 0
    failed = 0
    for test in TESTS:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test.__name__}: {e}")
            failed += 1
    print(f"\n--- Results: {passed} passing, {failed} failing ---\n")
    sys.exit(0 if failed == 0 else 1)
