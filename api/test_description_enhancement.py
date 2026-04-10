#!/usr/bin/env python
"""Tests for description generation enhancement feature.

Spec clauses covered:
- [SC-1] Generate from scratch when existing_description is empty/absent
- [SC-2] Enhance mode triggered when existing_description is non-empty
- [SC-3] existing_description whitespace-only treated as empty (generate from scratch)
- [SC-4] API_WORLD_DESCRIPTION_ENHANCE_TEMPLATE exists in PromptTemplates
- [SC-5] Enhance template contains {existing_description} placeholder
- [SC-6] Route passes existing_description to enhance template when present
- [SC-7] Route uses base template when existing_description absent
"""

import sys
import os
import json
from unittest.mock import patch, MagicMock

os.environ['TEST_MODE'] = '1'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_gpt_response(text):
    """Build a minimal mock OpenAI chat completion response."""
    choice = MagicMock()
    choice.message.content = text
    resp = MagicMock()
    resp.choices = [choice]
    return resp


# ---------------------------------------------------------------------------
# [SC-4] Prompt template existence
# ---------------------------------------------------------------------------

def test_enhance_template_exists():
    """[SC-4] API_WORLD_DESCRIPTION_ENHANCE_TEMPLATE must exist in PromptTemplates."""
    print("Testing enhance template existence...")
    from ai.prompts import PromptTemplates
    assert hasattr(PromptTemplates, 'API_WORLD_DESCRIPTION_ENHANCE_TEMPLATE'), \
        "API_WORLD_DESCRIPTION_ENHANCE_TEMPLATE not found in PromptTemplates"
    print("✅ Enhance template exists")


def test_enhance_template_has_placeholder():
    """[SC-5] Enhance template must contain {existing_description} placeholder."""
    print("Testing enhance template placeholders...")
    from ai.prompts import PromptTemplates
    tpl = PromptTemplates.API_WORLD_DESCRIPTION_ENHANCE_TEMPLATE
    assert '{existing_description}' in tpl, \
        "Template missing {existing_description} placeholder"
    assert '{world_name}' in tpl, "Template missing {world_name} placeholder"
    assert '{world_type}' in tpl, "Template missing {world_type} placeholder"
    print("✅ Enhance template has all required placeholders")


def test_enhance_template_format():
    """[SC-5] Enhance template must format correctly without KeyError."""
    print("Testing enhance template formatting...")
    from ai.prompts import PromptTemplates
    result = PromptTemplates.API_WORLD_DESCRIPTION_ENHANCE_TEMPLATE.format(
        world_type='fantasy',
        world_name='Test World',
        existing_description='A basic world with magic.'
    )
    assert 'Test World' in result
    assert 'A basic world with magic.' in result
    print("✅ Enhance template formats correctly")


# ---------------------------------------------------------------------------
# [SC-1] & [SC-7] Generate from scratch when no existing_description
# ---------------------------------------------------------------------------

def test_route_uses_base_template_when_no_existing_description():
    """[SC-1][SC-7] Route must use base template when existing_description absent."""
    print("Testing route uses base template when no existing_description...")
    import tempfile, os
    os.environ.pop('MONGODB_URI', None)
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()

    from interfaces.api_backend import APIBackend
    backend = APIBackend(storage_type='nosql', db_path=temp_db.name)
    client = backend.app.test_client()

    # Login
    resp = client.post('/api/auth/login',
                       json={'username': 'admin', 'password': 'Admin@123'})
    assert resp.status_code == 200
    token = resp.get_json()['token']

    captured_prompts = []

    def fake_create(**kwargs):
        msgs = kwargs.get('messages', [])
        captured_prompts.append(msgs[-1]['content'] if msgs else '')
        return _make_mock_gpt_response('Generated from scratch description.')

    with patch.object(backend, 'has_gpt', True), \
         patch.object(backend, '_ensure_gpt'), \
         patch.object(backend, 'gpt', create=True) as mock_gpt:
        mock_gpt.model = 'gpt-4o-mini'
        mock_gpt.client = MagicMock()
        mock_gpt.client.chat.completions.create.side_effect = fake_create

        resp = client.post(
            '/api/gpt/generate-description',
            json={'type': 'world', 'world_name': 'Eldoria', 'world_type': 'fantasy'},
            headers={'Authorization': f'Bearer {token}'}
        )

    assert resp.status_code == 200
    task_id = resp.get_json()['task_id']

    # Poll result (synchronous in test via direct thread join)
    import time
    result_data = None
    for _ in range(20):
        r = client.get(f'/api/gpt/results/{task_id}',
                       headers={'Authorization': f'Bearer {token}'})
        data = r.get_json()
        if data['status'] in ('completed', 'error'):
            result_data = data
            break
        time.sleep(0.1)

    assert result_data is not None and result_data['status'] == 'completed', \
        f"Task did not complete: {result_data}"

    # Base template should NOT contain existing description wording
    prompt_used = captured_prompts[0] if captured_prompts else ''
    assert 'Expand and enrich' not in prompt_used, \
        "Route incorrectly used enhance template when no existing_description provided"
    print("✅ Route uses base template when no existing_description")

    os.unlink(temp_db.name)


# ---------------------------------------------------------------------------
# [SC-2] & [SC-6] Enhance mode when existing_description non-empty
# ---------------------------------------------------------------------------

def test_route_uses_enhance_template_when_existing_description_provided():
    """[SC-2][SC-6] Route must use enhance template when existing_description non-empty."""
    print("Testing route uses enhance template when existing_description provided...")
    import tempfile, os
    os.environ.pop('MONGODB_URI', None)
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()

    from interfaces.api_backend import APIBackend
    backend = APIBackend(storage_type='nosql', db_path=temp_db.name)
    client = backend.app.test_client()

    resp = client.post('/api/auth/login',
                       json={'username': 'admin', 'password': 'Admin@123'})
    assert resp.status_code == 200
    token = resp.get_json()['token']

    captured_prompts = []

    def fake_create(**kwargs):
        msgs = kwargs.get('messages', [])
        captured_prompts.append(msgs[-1]['content'] if msgs else '')
        return _make_mock_gpt_response('Enhanced description.')

    with patch.object(backend, 'has_gpt', True), \
         patch.object(backend, '_ensure_gpt'), \
         patch.object(backend, 'gpt', create=True) as mock_gpt:
        mock_gpt.model = 'gpt-4o-mini'
        mock_gpt.client = MagicMock()
        mock_gpt.client.chat.completions.create.side_effect = fake_create

        resp = client.post(
            '/api/gpt/generate-description',
            json={
                'type': 'world',
                'world_name': 'Eldoria',
                'world_type': 'fantasy',
                'existing_description': 'Thế giới tu tiên cổ đại.'
            },
            headers={'Authorization': f'Bearer {token}'}
        )

    assert resp.status_code == 200
    task_id = resp.get_json()['task_id']

    import time
    result_data = None
    for _ in range(20):
        r = client.get(f'/api/gpt/results/{task_id}',
                       headers={'Authorization': f'Bearer {token}'})
        data = r.get_json()
        if data['status'] in ('completed', 'error'):
            result_data = data
            break
        time.sleep(0.1)

    assert result_data is not None and result_data['status'] == 'completed', \
        f"Task did not complete: {result_data}"

    prompt_used = captured_prompts[0] if captured_prompts else ''
    assert 'Thế giới tu tiên cổ đại.' in prompt_used, \
        "Enhance template did not include existing_description in prompt"
    assert 'Expand and enrich' in prompt_used, \
        "Route did not use enhance template when existing_description was provided"
    print("✅ Route uses enhance template when existing_description provided")

    os.unlink(temp_db.name)


# ---------------------------------------------------------------------------
# [SC-3] Whitespace-only treated as empty
# ---------------------------------------------------------------------------

def test_whitespace_only_existing_description_treated_as_empty():
    """[SC-3] Whitespace-only existing_description must use base template."""
    print("Testing whitespace-only existing_description treated as empty...")
    import tempfile, os
    os.environ.pop('MONGODB_URI', None)
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()

    from interfaces.api_backend import APIBackend
    backend = APIBackend(storage_type='nosql', db_path=temp_db.name)
    client = backend.app.test_client()

    resp = client.post('/api/auth/login',
                       json={'username': 'admin', 'password': 'Admin@123'})
    assert resp.status_code == 200
    token = resp.get_json()['token']

    captured_prompts = []

    def fake_create(**kwargs):
        msgs = kwargs.get('messages', [])
        captured_prompts.append(msgs[-1]['content'] if msgs else '')
        return _make_mock_gpt_response('Generated description.')

    with patch.object(backend, 'has_gpt', True), \
         patch.object(backend, '_ensure_gpt'), \
         patch.object(backend, 'gpt', create=True) as mock_gpt:
        mock_gpt.model = 'gpt-4o-mini'
        mock_gpt.client = MagicMock()
        mock_gpt.client.chat.completions.create.side_effect = fake_create

        resp = client.post(
            '/api/gpt/generate-description',
            json={
                'type': 'world',
                'world_name': 'Eldoria',
                'world_type': 'fantasy',
                'existing_description': '   \n\t  '
            },
            headers={'Authorization': f'Bearer {token}'}
        )

    assert resp.status_code == 200
    task_id = resp.get_json()['task_id']

    import time
    result_data = None
    for _ in range(20):
        r = client.get(f'/api/gpt/results/{task_id}',
                       headers={'Authorization': f'Bearer {token}'})
        data = r.get_json()
        if data['status'] in ('completed', 'error'):
            result_data = data
            break
        time.sleep(0.1)

    assert result_data is not None and result_data['status'] == 'completed', \
        f"Task did not complete: {result_data}"

    prompt_used = captured_prompts[0] if captured_prompts else ''
    assert 'Expand and enrich' not in prompt_used, \
        "Route incorrectly used enhance template for whitespace-only existing_description"
    print("✅ Whitespace-only existing_description treated as empty")

    os.unlink(temp_db.name)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(__file__))
    tests = [
        test_enhance_template_exists,
        test_enhance_template_has_placeholder,
        test_enhance_template_format,
        test_route_uses_base_template_when_no_existing_description,
        test_route_uses_enhance_template_when_existing_description_provided,
        test_whitespace_only_existing_description_treated_as_empty,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"❌ {t.__name__}: {e}")
            failed += 1
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
