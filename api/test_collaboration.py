#!/usr/bin/env python
"""Tests for Collaborative Novel Writing feature.

Covers all spec clauses for:
  SUB-1 — Auto-save Writing Process
  SUB-2 — Co-Author Permissions
  SUB-3 — Dedicated Story Editor Page (API layer)
  SUB-4 — Novel Structure

All tests are expected to FAIL (red state) until implementation is complete.
"""

import sys
import os
import json
import tempfile

os.environ['TEST_MODE'] = '1'

from interfaces.api_backend import APIBackend


def _create_test_app():
    os.environ.pop('MONGODB_URI', None)
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    path = temp_db.name
    temp_db.close()
    backend = APIBackend(storage_type='nosql', db_path=path)
    return backend, path


def _register_and_login(client, username, email, password='Test@1234'):
    resp = client.post('/api/auth/register', json={
        'username': username, 'email': email, 'password': password
    }, content_type='application/json')
    assert resp.status_code == 201, f"Register failed for {username}: {resp.data}"
    return resp.get_json()['token']


def _login(client, username, password='Test@1234'):
    resp = client.post('/api/auth/login', json={
        'username': username, 'password': password
    }, content_type='application/json')
    assert resp.status_code == 200, f"Login failed for {username}: {resp.data}"
    return resp.get_json()['token']


def _auth(token):
    return {'Authorization': f'Bearer {token}'}


def _create_world(client, token, name='Test World'):
    resp = client.post('/api/worlds', json={
        'name': name,
        'world_type': 'fantasy',
        'description': 'A world for collaborative testing purposes.',
        'visibility': 'private'
    }, headers=_auth(token), content_type='application/json')
    assert resp.status_code == 201, f"Create world failed: {resp.data}"
    return resp.get_json()['data']['world_id']


def _create_story(client, token, world_id, title='Chapter One'):
    resp = client.post('/api/stories', json={
        'title': title,
        'world_id': world_id,
        'description': 'Once upon a time...',
        'visibility': 'private'
    }, headers=_auth(token), content_type='application/json')
    assert resp.status_code == 201, f"Create story failed: {resp.data}"
    return resp.get_json()['data']['story_id']


# =============================================================================
# SUB-1 — Auto-save Writing Process
# =============================================================================

def test_autosave_patch_content(client):
    """BR-1.1, BR-1.2 — Owner can PATCH story content; updated_at is refreshed."""
    print("\n[SUB-1] Testing auto-save PATCH content...")
    token = _register_and_login(client, 'writer1', 'writer1@example.com')
    world_id = _create_world(client, token)
    story_id = _create_story(client, token, world_id)

    resp = client.patch(f'/api/stories/{story_id}',
        json={'content': 'It was a dark and stormy night.'},
        headers=_auth(token), content_type='application/json')
    assert resp.status_code == 200, f"Auto-save PATCH failed: {resp.data}"
    data = resp.get_json()['data']
    assert data['story_id'] == story_id
    assert 'updated_at' in data
    print("✅ SUB-1: auto-save PATCH content passed")


def test_autosave_requires_auth(client):
    """BR-1.1 — Unauthenticated PATCH is rejected with 401."""
    print("\n[SUB-1] Testing auto-save auth enforcement...")
    token = _register_and_login(client, 'writer1b', 'writer1b@example.com')
    world_id = _create_world(client, token)
    story_id = _create_story(client, token, world_id)

    resp = client.patch(f'/api/stories/{story_id}',
        json={'content': 'No auth content.'},
        content_type='application/json')
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
    print("✅ SUB-1: auth enforcement passed")


def test_autosave_stranger_cannot_save(client):
    """BR-1.1 — A non-co-author cannot auto-save another user's story."""
    print("\n[SUB-1] Testing auto-save permission: stranger blocked...")
    owner_token = _register_and_login(client, 'owner1', 'owner1@example.com')
    stranger_token = _register_and_login(client, 'stranger1', 'stranger1@example.com')
    world_id = _create_world(client, owner_token)
    story_id = _create_story(client, owner_token, world_id)

    resp = client.patch(f'/api/stories/{story_id}',
        json={'content': 'Hacked content.'},
        headers=_auth(stranger_token), content_type='application/json')
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
    print("✅ SUB-1: stranger blocked from auto-save passed")


def test_autosave_deleted_story_returns_404(client):
    """EC-1.3 — Saving to a deleted story returns 404."""
    print("\n[SUB-1] Testing auto-save on deleted story...")
    token = _register_and_login(client, 'writer1c', 'writer1c@example.com')
    world_id = _create_world(client, token)
    story_id = _create_story(client, token, world_id)

    # Delete the story
    del_resp = client.delete(f'/api/stories/{story_id}', headers=_auth(token))
    assert del_resp.status_code == 200, f"Delete failed: {del_resp.data}"

    resp = client.patch(f'/api/stories/{story_id}',
        json={'content': 'Ghost content.'},
        headers=_auth(token), content_type='application/json')
    assert resp.status_code == 404, f"Expected 404 for deleted story, got {resp.status_code}"
    print("✅ SUB-1: 404 on deleted story passed")


# =============================================================================
# SUB-2 — Co-Author Permissions
# =============================================================================

def test_invite_coauthor(client):
    """BR-2.1 — Owner can invite a user as co_author."""
    print("\n[SUB-2] Testing invite co-author...")
    owner_token = _register_and_login(client, 'owner2', 'owner2@example.com')
    _register_and_login(client, 'coauthor2', 'coauthor2@example.com')
    world_id = _create_world(client, owner_token)

    resp = client.post(f'/api/worlds/{world_id}/collaborators',
        json={'username_or_email': 'coauthor2', 'role': 'co_author'},
        headers=_auth(owner_token), content_type='application/json')
    assert resp.status_code == 201, f"Invite co-author failed: {resp.data}"
    data = resp.get_json()['data']
    assert 'invitation_id' in data
    print("✅ SUB-2: invite co-author passed")


def test_invite_nonexistent_user_returns_404(client):
    """EC-2.1 — Inviting a non-existent user returns 404."""
    print("\n[SUB-2] Testing invite non-existent user...")
    owner_token = _register_and_login(client, 'owner2b', 'owner2b@example.com')
    world_id = _create_world(client, owner_token)

    resp = client.post(f'/api/worlds/{world_id}/collaborators',
        json={'username_or_email': 'ghost_user_xyz', 'role': 'co_author'},
        headers=_auth(owner_token), content_type='application/json')
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
    print("✅ SUB-2: invite non-existent user 404 passed")


def test_owner_cannot_invite_themselves(client):
    """EC-2.2 — Owner inviting themselves returns 400."""
    print("\n[SUB-2] Testing owner self-invite blocked...")
    owner_token = _register_and_login(client, 'owner2c', 'owner2c@example.com')
    world_id = _create_world(client, owner_token)

    resp = client.post(f'/api/worlds/{world_id}/collaborators',
        json={'username_or_email': 'owner2c', 'role': 'co_author'},
        headers=_auth(owner_token), content_type='application/json')
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
    print("✅ SUB-2: self-invite blocked passed")


def test_duplicate_invite_returns_409(client):
    """BR-2.4 — Inviting an already-invited user returns 409."""
    print("\n[SUB-2] Testing duplicate invite returns 409...")
    owner_token = _register_and_login(client, 'owner2d', 'owner2d@example.com')
    _register_and_login(client, 'coauthor2d', 'coauthor2d@example.com')
    world_id = _create_world(client, owner_token)

    client.post(f'/api/worlds/{world_id}/collaborators',
        json={'username_or_email': 'coauthor2d', 'role': 'co_author'},
        headers=_auth(owner_token), content_type='application/json')

    resp = client.post(f'/api/worlds/{world_id}/collaborators',
        json={'username_or_email': 'coauthor2d', 'role': 'co_author'},
        headers=_auth(owner_token), content_type='application/json')
    assert resp.status_code == 409, f"Expected 409 for duplicate invite, got {resp.status_code}"
    print("✅ SUB-2: duplicate invite 409 passed")


def test_coauthor_can_edit_story_after_accept(client):
    """BR-2.5 — Co-author can PATCH a story after accepting invitation."""
    print("\n[SUB-2] Testing co-author can edit story after accept...")
    owner_token = _register_and_login(client, 'owner2e', 'owner2e@example.com')
    coauthor_token = _register_and_login(client, 'coauthor2e', 'coauthor2e@example.com')
    world_id = _create_world(client, owner_token)
    story_id = _create_story(client, owner_token, world_id)

    # Owner invites
    inv_resp = client.post(f'/api/worlds/{world_id}/collaborators',
        json={'username_or_email': 'coauthor2e', 'role': 'co_author'},
        headers=_auth(owner_token), content_type='application/json')
    assert inv_resp.status_code == 201
    invitation_id = inv_resp.get_json()['data']['invitation_id']

    # Co-author accepts
    accept_resp = client.post(f'/api/users/me/invitations/{invitation_id}/accept',
        headers=_auth(coauthor_token), content_type='application/json')
    assert accept_resp.status_code == 200, f"Accept failed: {accept_resp.data}"

    # Co-author edits story
    edit_resp = client.patch(f'/api/stories/{story_id}',
        json={'content': 'Co-author was here.'},
        headers=_auth(coauthor_token), content_type='application/json')
    assert edit_resp.status_code == 200, f"Co-author edit failed: {edit_resp.data}"
    print("✅ SUB-2: co-author can edit story after accept passed")


def test_list_collaborators(client):
    """BR-2.1 — GET /collaborators lists co-authors of a world."""
    print("\n[SUB-2] Testing list collaborators...")
    owner_token = _register_and_login(client, 'owner2f', 'owner2f@example.com')
    _register_and_login(client, 'coauthor2f', 'coauthor2f@example.com')
    world_id = _create_world(client, owner_token)

    client.post(f'/api/worlds/{world_id}/collaborators',
        json={'username_or_email': 'coauthor2f', 'role': 'co_author'},
        headers=_auth(owner_token), content_type='application/json')

    # Co-author must accept before appearing in the list
    inv_resp = client.get('/api/users/me/invitations',
        headers=_auth(_login(client, 'coauthor2f')))
    assert inv_resp.status_code == 200
    invitations = inv_resp.get_json()['data']
    assert len(invitations) > 0
    invitation_id = invitations[0]['invitation_id']
    client.post(f'/api/users/me/invitations/{invitation_id}/accept',
        headers=_auth(_login(client, 'coauthor2f')))

    resp = client.get(f'/api/worlds/{world_id}/collaborators',
        headers=_auth(owner_token))
    assert resp.status_code == 200, f"List collaborators failed: {resp.data}"
    collaborators = resp.get_json()['data']
    assert any(c['username'] == 'coauthor2f' for c in collaborators)
    print("✅ SUB-2: list collaborators passed")


def test_revoke_coauthor(client):
    """BR-2.1 — Owner can revoke co-author; revoked user loses edit access."""
    print("\n[SUB-2] Testing revoke co-author...")
    owner_token = _register_and_login(client, 'owner2g', 'owner2g@example.com')
    coauthor_token = _register_and_login(client, 'coauthor2g', 'coauthor2g@example.com')
    world_id = _create_world(client, owner_token)
    story_id = _create_story(client, owner_token, world_id)

    # Invite and accept
    inv_resp = client.post(f'/api/worlds/{world_id}/collaborators',
        json={'username_or_email': 'coauthor2g', 'role': 'co_author'},
        headers=_auth(owner_token), content_type='application/json')
    invitation_id = inv_resp.get_json()['data']['invitation_id']
    client.post(f'/api/users/me/invitations/{invitation_id}/accept',
        headers=_auth(coauthor_token))

    # Get co-author user_id from collaborator list
    collab_resp = client.get(f'/api/worlds/{world_id}/collaborators',
        headers=_auth(owner_token))
    collaborators = collab_resp.get_json()['data']
    coauthor_user_id = next(c['user_id'] for c in collaborators if c['username'] == 'coauthor2g')

    # Revoke
    revoke_resp = client.delete(f'/api/worlds/{world_id}/collaborators/{coauthor_user_id}',
        headers=_auth(owner_token))
    assert revoke_resp.status_code == 200, f"Revoke failed: {revoke_resp.data}"

    # Revoked co-author can no longer edit
    edit_resp = client.patch(f'/api/stories/{story_id}',
        json={'content': 'Should be blocked.'},
        headers=_auth(coauthor_token), content_type='application/json')
    assert edit_resp.status_code == 403, f"Expected 403 after revoke, got {edit_resp.status_code}"
    print("✅ SUB-2: revoke co-author passed")


def test_non_owner_cannot_invite(client):
    """BR-2.1 — Only the world owner may invite co-authors."""
    print("\n[SUB-2] Testing non-owner cannot invite...")
    owner_token = _register_and_login(client, 'owner2h', 'owner2h@example.com')
    coauthor_token = _register_and_login(client, 'coauthor2h', 'coauthor2h@example.com')
    _register_and_login(client, 'third2h', 'third2h@example.com')
    world_id = _create_world(client, owner_token)

    # Make coauthor2h a co-author
    inv_resp = client.post(f'/api/worlds/{world_id}/collaborators',
        json={'username_or_email': 'coauthor2h', 'role': 'co_author'},
        headers=_auth(owner_token), content_type='application/json')
    invitation_id = inv_resp.get_json()['data']['invitation_id']
    client.post(f'/api/users/me/invitations/{invitation_id}/accept',
        headers=_auth(coauthor_token))

    # Co-author tries to invite a third person — should be blocked
    resp = client.post(f'/api/worlds/{world_id}/collaborators',
        json={'username_or_email': 'third2h', 'role': 'co_author'},
        headers=_auth(coauthor_token), content_type='application/json')
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
    print("✅ SUB-2: non-owner cannot invite passed")


# =============================================================================
# SUB-3 — Story Editor API (paraphrase endpoint)
# =============================================================================

def test_paraphrase_endpoint_exists(client):
    """BR-3.3 — POST /api/gpt/paraphrase accepts text + mode."""
    print("\n[SUB-3] Testing paraphrase endpoint exists...")
    token = _register_and_login(client, 'writer3', 'writer3@example.com')

    resp = client.post('/api/gpt/paraphrase',
        json={'text': 'He walked into the room.', 'mode': 'paraphrase'},
        headers=_auth(token), content_type='application/json')
    # Should return 200 with suggestions list (will fail until implemented)
    assert resp.status_code == 200, f"Paraphrase endpoint failed: {resp.data}"
    data = resp.get_json()['data']
    assert 'suggestions' in data
    assert isinstance(data['suggestions'], list)
    assert len(data['suggestions']) == 3
    print("✅ SUB-3: paraphrase endpoint passed")


def test_paraphrase_expand_mode(client):
    """BR-3.3 — mode=expand also returns suggestions."""
    print("\n[SUB-3] Testing paraphrase expand mode...")
    token = _register_and_login(client, 'writer3b', 'writer3b@example.com')

    resp = client.post('/api/gpt/paraphrase',
        json={'text': 'The dragon roared.', 'mode': 'expand'},
        headers=_auth(token), content_type='application/json')
    assert resp.status_code == 200, f"Expand mode failed: {resp.data}"
    data = resp.get_json()['data']
    assert 'suggestions' in data
    print("✅ SUB-3: paraphrase expand mode passed")


def test_paraphrase_requires_auth(client):
    """BR-3.1 — Paraphrase endpoint requires authentication."""
    print("\n[SUB-3] Testing paraphrase requires auth...")
    resp = client.post('/api/gpt/paraphrase',
        json={'text': 'He walked.', 'mode': 'paraphrase'},
        content_type='application/json')
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
    print("✅ SUB-3: paraphrase requires auth passed")


def test_paraphrase_invalid_mode_rejected(client):
    """BR-3.3 — Invalid mode value is rejected with 400."""
    print("\n[SUB-3] Testing paraphrase invalid mode...")
    token = _register_and_login(client, 'writer3c', 'writer3c@example.com')

    resp = client.post('/api/gpt/paraphrase',
        json={'text': 'He walked.', 'mode': 'summarize'},
        headers=_auth(token), content_type='application/json')
    assert resp.status_code == 400, f"Expected 400 for invalid mode, got {resp.status_code}"
    print("✅ SUB-3: invalid mode rejected passed")


def test_paraphrase_missing_text_rejected(client):
    """BR-3.3 — Missing text field returns 400."""
    print("\n[SUB-3] Testing paraphrase missing text...")
    token = _register_and_login(client, 'writer3d', 'writer3d@example.com')

    resp = client.post('/api/gpt/paraphrase',
        json={'mode': 'paraphrase'},
        headers=_auth(token), content_type='application/json')
    assert resp.status_code == 400, f"Expected 400 for missing text, got {resp.status_code}"
    print("✅ SUB-3: missing text rejected passed")


# =============================================================================
# SUB-4 — Novel Structure
# =============================================================================

def test_create_novel(client):
    """BR-4.1 — PUT /api/worlds/{id}/novel creates novel metadata."""
    print("\n[SUB-4] Testing create novel...")
    token = _register_and_login(client, 'novelist4', 'novelist4@example.com')
    world_id = _create_world(client, token)

    resp = client.put(f'/api/worlds/{world_id}/novel',
        json={'title': 'The Great Novel', 'description': 'An epic tale.'},
        headers=_auth(token), content_type='application/json')
    assert resp.status_code == 200, f"Create novel failed: {resp.data}"
    data = resp.get_json()['data']
    assert data['title'] == 'The Great Novel'
    assert data['description'] == 'An epic tale.'
    print("✅ SUB-4: create novel passed")


def test_get_novel_with_chapters(client):
    """BR-4.2 — GET /api/worlds/{id}/novel returns chapters in order."""
    print("\n[SUB-4] Testing get novel with chapters...")
    token = _register_and_login(client, 'novelist4b', 'novelist4b@example.com')
    world_id = _create_world(client, token)
    story_id_1 = _create_story(client, token, world_id, title='Chapter One')
    story_id_2 = _create_story(client, token, world_id, title='Chapter Two')

    client.put(f'/api/worlds/{world_id}/novel',
        json={'title': 'My Novel'},
        headers=_auth(token), content_type='application/json')

    # Assign chapter numbers
    client.patch(f'/api/stories/{story_id_1}',
        json={'chapter_number': 1},
        headers=_auth(token), content_type='application/json')
    client.patch(f'/api/stories/{story_id_2}',
        json={'chapter_number': 2},
        headers=_auth(token), content_type='application/json')

    resp = client.get(f'/api/worlds/{world_id}/novel',
        headers=_auth(token))
    assert resp.status_code == 200, f"Get novel failed: {resp.data}"
    data = resp.get_json()['data']
    assert 'chapters' in data
    assert 'total_word_count' in data
    chapters = data['chapters']
    assert len(chapters) == 2
    assert chapters[0]['chapter_number'] == 1
    assert chapters[1]['chapter_number'] == 2
    print("✅ SUB-4: get novel with chapters passed")


def test_reorder_chapters(client):
    """BR-4.2 — PATCH /novel/chapters reorders and renumbers contiguously."""
    print("\n[SUB-4] Testing reorder chapters...")
    token = _register_and_login(client, 'novelist4c', 'novelist4c@example.com')
    world_id = _create_world(client, token)
    s1 = _create_story(client, token, world_id, title='First')
    s2 = _create_story(client, token, world_id, title='Second')
    s3 = _create_story(client, token, world_id, title='Third')

    client.put(f'/api/worlds/{world_id}/novel',
        json={'title': 'Reorder Test'},
        headers=_auth(token), content_type='application/json')

    # Reorder: put s3 first, then s1, then s2
    resp = client.patch(f'/api/worlds/{world_id}/novel/chapters',
        json={'order': [s3, s1, s2]},
        headers=_auth(token), content_type='application/json')
    assert resp.status_code == 200, f"Reorder chapters failed: {resp.data}"
    chapters = resp.get_json()['data']['chapters']
    order_map = {c['story_id']: c['chapter_number'] for c in chapters}
    assert order_map[s3] == 1
    assert order_map[s1] == 2
    assert order_map[s2] == 3
    print("✅ SUB-4: reorder chapters passed")


def test_novel_empty_world(client):
    """EC-4.1 — Novel overview on a world with no stories returns empty chapters."""
    print("\n[SUB-4] Testing novel on empty world...")
    token = _register_and_login(client, 'novelist4d', 'novelist4d@example.com')
    world_id = _create_world(client, token)

    client.put(f'/api/worlds/{world_id}/novel',
        json={'title': 'Empty Novel'},
        headers=_auth(token), content_type='application/json')

    resp = client.get(f'/api/worlds/{world_id}/novel',
        headers=_auth(token))
    assert resp.status_code == 200, f"Empty novel failed: {resp.data}"
    data = resp.get_json()['data']
    assert data['chapters'] == []
    assert data['total_word_count'] == 0
    print("✅ SUB-4: novel empty world passed")


def test_coauthor_cannot_manage_novel_without_accept(client):
    """BR-4.1 — A user who has not accepted co-author invitation cannot manage novel."""
    print("\n[SUB-4] Testing non-collaborator blocked from novel management...")
    owner_token = _register_and_login(client, 'owner4e', 'owner4e@example.com')
    other_token = _register_and_login(client, 'other4e', 'other4e@example.com')
    world_id = _create_world(client, owner_token)

    resp = client.put(f'/api/worlds/{world_id}/novel',
        json={'title': 'Hijacked Novel'},
        headers=_auth(other_token), content_type='application/json')
    assert resp.status_code == 403, f"Expected 403 for non-collaborator, got {resp.status_code}"
    print("✅ SUB-4: non-collaborator blocked from novel management passed")


def test_chapter_number_in_story_model(client):
    """BR-4.2 — Story model serializes chapter_number field."""
    print("\n[SUB-4] Testing chapter_number in story model...")
    from core.models import Story
    story = Story(title='Ch1', content='Content', world_id='world-1', chapter_number=3)
    d = story.to_dict()
    assert d['chapter_number'] == 3
    story2 = Story.from_dict(d)
    assert story2.chapter_number == 3
    print("✅ SUB-4: chapter_number in story model passed")


def test_updated_at_in_story_model(client):
    """BR-1.2 — Story model serializes updated_at field."""
    print("\n[SUB-4] Testing updated_at in story model...")
    from core.models import Story
    story = Story(title='Ts', content='C', world_id='w-1')
    d = story.to_dict()
    assert 'updated_at' in d
    assert d['updated_at'] is not None
    print("✅ SUB-1: updated_at in story model passed")


def test_co_authors_in_world_model(client):
    """BR-2.1 — World model serializes co_authors field."""
    print("\n[SUB-2] Testing co_authors in world model...")
    from core.models import World
    world = World(name='W', description='A fictional realm for testing.', co_authors=['user-1', 'user-2'])
    d = world.to_dict()
    assert 'co_authors' in d
    assert 'user-1' in d['co_authors']
    world2 = World.from_dict(d)
    assert world2.co_authors == ['user-1', 'user-2']
    print("✅ SUB-2: co_authors in world model passed")


def test_novel_in_world_model(client):
    """BR-4.1 — World model serializes novel metadata block."""
    print("\n[SUB-4] Testing novel in world model...")
    from core.models import World
    novel_data = {'title': 'Epic', 'description': 'An adventure.', 'chapter_order': []}
    world = World(name='W', description='A fictional realm for testing.', novel=novel_data)
    d = world.to_dict()
    assert d['novel']['title'] == 'Epic'
    world2 = World.from_dict(d)
    assert world2.novel['title'] == 'Epic'
    print("✅ SUB-4: novel in world model passed")


def test_invitation_model_roundtrip(client):
    """BR-2.4 — Invitation model serializes and deserializes correctly."""
    print("\n[SUB-2] Testing Invitation model roundtrip...")
    from core.models import Invitation
    inv = Invitation(world_id='w-1', invited_by='user-owner', invitee_id='user-guest')
    d = inv.to_dict()
    assert d['status'] == 'pending'
    assert d['world_id'] == 'w-1'
    inv2 = Invitation.from_dict(d)
    assert inv2.invitation_id == inv.invitation_id
    assert inv2.status == 'pending'
    print("✅ SUB-2: Invitation model roundtrip passed")


# =============================================================================
# Runner
# =============================================================================

def run_all():
    backend, db_path = _create_test_app()
    app = backend.app
    passed = 0
    failed = 0
    errors = []

    # Model-only tests (no HTTP client needed — pass None)
    model_tests = [
        test_chapter_number_in_story_model,
        test_updated_at_in_story_model,
        test_co_authors_in_world_model,
        test_novel_in_world_model,
        test_invitation_model_roundtrip,
    ]

    http_tests = [
        test_autosave_patch_content,
        test_autosave_requires_auth,
        test_autosave_stranger_cannot_save,
        test_autosave_deleted_story_returns_404,
        test_invite_coauthor,
        test_invite_nonexistent_user_returns_404,
        test_owner_cannot_invite_themselves,
        test_duplicate_invite_returns_409,
        test_coauthor_can_edit_story_after_accept,
        test_list_collaborators,
        test_revoke_coauthor,
        test_non_owner_cannot_invite,
        test_paraphrase_endpoint_exists,
        test_paraphrase_expand_mode,
        test_paraphrase_requires_auth,
        test_paraphrase_invalid_mode_rejected,
        test_paraphrase_missing_text_rejected,
        test_create_novel,
        test_get_novel_with_chapters,
        test_reorder_chapters,
        test_novel_empty_world,
        test_coauthor_cannot_manage_novel_without_accept,
    ]

    print("\n" + "=" * 60)
    print("  COLLABORATION TESTS — expecting RED state")
    print("=" * 60)

    with app.test_client() as client:
        for test_fn in model_tests:
            try:
                test_fn(None)
                passed += 1
            except Exception as e:
                failed += 1
                errors.append((test_fn.__name__, str(e)))
                print(f"❌ {test_fn.__name__}: {e}")

        for test_fn in http_tests:
            try:
                test_fn(client)
                passed += 1
            except Exception as e:
                failed += 1
                errors.append((test_fn.__name__, str(e)))
                print(f"❌ {test_fn.__name__}: {e}")

    total = passed + failed
    print("\n" + "=" * 60)
    print(f"  Results: {passed}/{total} passing  |  {failed} failing")
    print("=" * 60)

    if errors:
        print("\nFailing tests:")
        for name, err in errors:
            print(f"  - {name}: {err}")

    import os as _os
    try:
        _os.unlink(db_path)
    except Exception:
        pass

    return failed


if __name__ == '__main__':
    failing = run_all()
    sys.exit(0 if failing > 0 else 1)  # exit 0 = red state confirmed
