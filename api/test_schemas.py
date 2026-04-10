#!/usr/bin/env python
"""Tests for request validation schemas.

Covers: world_schemas, story_schemas, auth_schemas, event_schemas,
        gpt_schemas, admin_schemas.

Run:
    python api/test_schemas.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from marshmallow import ValidationError

from schemas.world_schemas import (
    CreateWorldSchema,
    UpdateWorldSchema,
    ListWorldsQuerySchema,
    CreateEntitySchema,
    UpdateEntitySchema,
    AddCollaboratorSchema,
    UpdateNovelSchema,
    ReorderChaptersSchema,
)
from schemas.story_schemas import (
    CreateStorySchema,
    UpdateStorySchema,
    ListStoriesQuerySchema,
    LinkEntitiesSchema,
    AddStoryEventSchema,
)
from schemas.auth_schemas import (
    RegisterSchema,
    LoginSchema,
    GoogleAuthSchema,
    ChangePasswordSchema,
    UpdateProfileSchema,
)
from schemas.event_schemas import (
    UpdateEventSchema,
    AddEventConnectionSchema,
)
from schemas.gpt_schemas import GptParaphraseSchema
from schemas.admin_schemas import (
    ChangeUserRoleSchema,
    BanUserSchema,
    ListUsersQuerySchema,
)

PASS = 0
FAIL = 0


def ok(msg):
    global PASS
    PASS += 1
    print(f"  ✅ {msg}")


def fail(msg, err=""):
    global FAIL
    FAIL += 1
    print(f"  ❌ {msg}")
    if err:
        print(f"     → {err}")


def assert_valid(schema, data, label):
    """Assert that data loads without error."""
    try:
        schema.load(data)
        ok(label)
    except ValidationError as e:
        fail(label, str(e.messages))


def assert_invalid(schema, data, label, field=None):
    """Assert that data raises ValidationError, optionally on a specific field."""
    try:
        schema.load(data)
        fail(label + " (should have raised ValidationError)")
    except ValidationError as e:
        if field and field not in e.messages:
            fail(label + f" (expected error on '{field}', got {list(e.messages.keys())})")
        else:
            ok(label)


# ---------------------------------------------------------------------------
# world_schemas
# ---------------------------------------------------------------------------

def test_create_world():
    print("\n[CreateWorldSchema]")
    s = CreateWorldSchema()

    assert_valid(s, {
        "name": "Middle Earth",
        "world_type": "fantasy",
        "description": "A rich fantasy world with many races."
    }, "valid minimal payload")

    assert_valid(s, {
        "name": "Terra",
        "world_type": "sci-fi",
        "description": "A futuristic sci-fi setting.",
        "visibility": "public",
        "use_gpt": True,
    }, "valid full payload")

    assert_invalid(s, {
        "world_type": "fantasy",
        "description": "Missing name."
    }, "missing required 'name'", "name")

    assert_invalid(s, {
        "name": "Earth",
        "world_type": "fantasy",
        "description": "Too short"
    }, "description too short (< 10 chars)", "description")

    assert_invalid(s, {
        "name": "Earth",
        "world_type": "magic",          # ← invalid
        "description": "Unknown type should fail."
    }, "invalid world_type 'magic'", "world_type")

    assert_invalid(s, {
        "name": "Earth",
        "world_type": "fantasy",
        "description": "Valid description here.",
        "visibility": "secret"          # ← invalid
    }, "invalid visibility 'secret'", "visibility")

    assert_invalid(s, {
        "name": "",                      # ← empty
        "world_type": "fantasy",
        "description": "Valid description here."
    }, "empty name rejected", "name")

    assert_invalid(s, {
        "name": "A" * 101,             # ← too long
        "world_type": "fantasy",
        "description": "Valid description here."
    }, "name exceeds 100 chars", "name")


def test_update_world():
    print("\n[UpdateWorldSchema]")
    s = UpdateWorldSchema()

    assert_valid(s, {"name": "New Name"}, "valid single field update")
    assert_valid(s, {"visibility": "public"}, "valid visibility update")
    assert_invalid(s, {}, "empty payload rejected", "_schema")


def test_list_worlds_query():
    print("\n[ListWorldsQuerySchema]")
    s = ListWorldsQuerySchema()

    assert_valid(s, {}, "empty params — all defaults")
    assert_valid(s, {"page": "2", "per_page": "50"}, "string ints coerced")
    assert_invalid(s, {"page": "0"}, "page=0 rejected", "page")
    assert_invalid(s, {"per_page": "101"}, "per_page > 100 rejected", "per_page")
    assert_invalid(s, {"visibility": "deleted"}, "invalid visibility rejected", "visibility")


def test_create_entity():
    print("\n[CreateEntitySchema]")
    s = CreateEntitySchema()

    assert_valid(s, {
        "name": "Gandalf",
        "entity_type": "character",
        "description": "A wizard."
    }, "valid character entity")

    assert_valid(s, {
        "name": "Ring",
        "entity_type": "object",
        "description": "Precious ring."
    }, "valid object entity")

    # description has load_default='' so it is optional
    assert_valid(s, {
        "name": "Gandalf",
        "entity_type": "character"
    }, "description optional (load_default='')")

    # Known issue: 'location' and 'concept' accepted by schema but
    # semantically incorrect — Location has its own model.
    assert_valid(s, {
        "name": "Shire",
        "entity_type": "location",
        "description": "A peaceful place."
    }, "entity_type='location' currently accepted (known schema issue)")

    assert_invalid(s, {
        "name": "Peace",
        "entity_type": "idea",          # ← not in OneOf list
        "description": "An abstract idea."
    }, "invalid entity_type 'idea' rejected", "entity_type")


def test_update_entity():
    print("\n[UpdateEntitySchema]")
    s = UpdateEntitySchema()

    assert_valid(s, {"name": "Bilbo"}, "valid single field update")
    assert_invalid(s, {}, "empty payload rejected", "_schema")


def test_add_collaborator():
    print("\n[AddCollaboratorSchema]")
    s = AddCollaboratorSchema()

    assert_valid(s, {"username_or_email": "user@example.com"}, "valid email")
    assert_valid(s, {"username_or_email": "johndoe"}, "valid username")
    assert_invalid(s, {}, "missing required field", "username_or_email")
    assert_invalid(s, {
        "username_or_email": "user",
        "role": "viewer"                # ← only 'co_author' allowed
    }, "invalid role rejected", "role")


def test_reorder_chapters():
    print("\n[ReorderChaptersSchema]")
    s = ReorderChaptersSchema()

    assert_valid(s, {"order": ["id1", "id2", "id3"]}, "valid order list")
    assert_invalid(s, {}, "missing required 'order'", "order")


# ---------------------------------------------------------------------------
# story_schemas
# ---------------------------------------------------------------------------

def test_create_story():
    print("\n[CreateStorySchema]")
    s = CreateStorySchema()

    assert_valid(s, {
        "title": "The Fellowship",
        "world_id": "world-123",
    }, "valid minimal payload")

    assert_valid(s, {
        "title": "The Fellowship",
        "world_id": "world-123",
        "genre": "adventure",
        "visibility": "public",
        "format": "markdown",
        "time_index": 50,
    }, "valid full payload")

    assert_invalid(s, {"world_id": "world-123"}, "missing required 'title'", "title")
    assert_invalid(s, {"title": "Story"}, "missing required 'world_id'", "world_id")

    assert_invalid(s, {
        "title": "Story",
        "world_id": "world-123",
        "visibility": "unlisted"        # ← invalid
    }, "invalid visibility rejected", "visibility")

    assert_invalid(s, {
        "title": "Story",
        "world_id": "world-123",
        "time_index": 101               # ← out of 0-100 range
    }, "time_index > 100 rejected", "time_index")

    assert_invalid(s, {
        "title": "Story",
        "world_id": "world-123",
        "time_index": -1                # ← out of 0-100 range
    }, "time_index < 0 rejected", "time_index")

    # Known bug: 'html' passes schema but Story model only supports 'plain'|'markdown'
    try:
        result = s.load({
            "title": "Story",
            "world_id": "world-123",
            "format": "html"
        })
        fail("format='html' accepted by schema — Story model does NOT support it (known bug)")
    except ValidationError:
        ok("format='html' correctly rejected")


def test_update_story():
    print("\n[UpdateStorySchema]")
    s = UpdateStorySchema()

    assert_valid(s, {"title": "New Title"}, "valid single field update")
    assert_valid(s, {"visibility": "public"}, "valid visibility update")
    assert_valid(s, {"chapter_number": 3}, "valid chapter_number update")
    assert_invalid(s, {}, "empty payload rejected", "_schema")
    assert_invalid(s, {"chapter_number": 0}, "chapter_number=0 rejected (min=1)", "chapter_number")
    assert_invalid(s, {"format": "html"}, "invalid format 'html' rejected", "format")


def test_list_stories_query():
    print("\n[ListStoriesQuerySchema]")
    s = ListStoriesQuerySchema()

    assert_valid(s, {}, "empty params — all defaults")
    assert_valid(s, {"world_id": "world-123", "visibility": "public"}, "valid filters")
    assert_invalid(s, {"per_page": "0"}, "per_page=0 rejected", "per_page")
    assert_invalid(s, {"visibility": "archived"}, "invalid visibility rejected", "visibility")


def test_link_entities():
    print("\n[LinkEntitiesSchema]")
    s = LinkEntitiesSchema()

    assert_valid(s, {}, "empty payload — uses defaults")
    assert_valid(s, {
        "characters": ["char-1", "char-2"],
        "locations": ["loc-1"],
        "auto_create": False
    }, "valid list of string IDs")


def test_add_story_event():
    print("\n[AddStoryEventSchema]")
    s = AddStoryEventSchema()

    assert_valid(s, {
        "event_type": "battle",
        "description": "A great battle ensued."
    }, "valid minimal payload")

    assert_invalid(s, {"description": "No event_type"}, "missing 'event_type'", "event_type")
    assert_invalid(s, {"event_type": "battle"}, "missing 'description'", "description")
    assert_invalid(s, {
        "event_type": "battle",
        "description": "test",
        "timestamp": -1                 # ← min=0
    }, "negative timestamp rejected", "timestamp")


# ---------------------------------------------------------------------------
# auth_schemas
# ---------------------------------------------------------------------------

def test_register():
    print("\n[RegisterSchema]")
    s = RegisterSchema()

    assert_valid(s, {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "Secure@123"
    }, "valid registration")

    assert_invalid(s, {
        "username": "jd",               # ← min=3
        "email": "john@example.com",
        "password": "Secure@123"
    }, "username too short rejected", "username")

    assert_invalid(s, {
        "username": "john doe",         # ← space not allowed
        "email": "john@example.com",
        "password": "Secure@123"
    }, "username with space rejected", "username")

    assert_invalid(s, {
        "username": "johndoe",
        "email": "not-an-email",
        "password": "Secure@123"
    }, "invalid email rejected", "email")

    assert_invalid(s, {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "short"             # ← weak
    }, "weak password rejected", "password")

    assert_invalid(s, {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "alllowercase1@"   # ← no uppercase
    }, "password without uppercase rejected", "password")

    assert_invalid(s, {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "ALLUPPERCASE1@"   # ← no lowercase
    }, "password without lowercase rejected", "password")

    assert_invalid(s, {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "NoNumbers@here"   # ← no digit
    }, "password without digit rejected", "password")

    assert_invalid(s, {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "NoSpecial123"     # ← no special char
    }, "password without special char rejected", "password")


def test_login():
    print("\n[LoginSchema]")
    s = LoginSchema()

    assert_valid(s, {"username": "johndoe", "password": "anypass"}, "valid login")
    assert_invalid(s, {"password": "anypass"}, "missing 'username'", "username")
    assert_invalid(s, {"username": "johndoe"}, "missing 'password'", "password")


def test_google_auth():
    print("\n[GoogleAuthSchema]")
    s = GoogleAuthSchema()

    assert_valid(s, {"credential": "eyJhbGciOiJSUzI1..."}, "valid credential token")
    assert_invalid(s, {}, "missing 'credential'", "credential")


def test_change_password():
    print("\n[ChangePasswordSchema]")
    s = ChangePasswordSchema()

    assert_valid(s, {
        "current_password": "OldPass@123",
        "new_password": "NewPass@456"
    }, "valid password change")

    assert_invalid(s, {
        "current_password": "OldPass@123"
    }, "missing 'new_password'", "new_password")

    assert_invalid(s, {
        "current_password": "OldPass@123",
        "new_password": "weak"          # ← fails strength check
    }, "weak new_password rejected", "new_password")


def test_update_profile():
    print("\n[UpdateProfileSchema]")
    s = UpdateProfileSchema()

    assert_valid(s, {"username": "new_name"}, "valid username update")
    assert_valid(s, {"email": "new@example.com"}, "valid email update")
    assert_valid(s, {"signature": "My bio"}, "valid signature update")
    assert_invalid(s, {}, "empty payload rejected", "_schema")
    assert_invalid(s, {"email": "bad-email"}, "invalid email rejected", "email")
    assert_invalid(s, {"username": "has space"}, "username with space rejected", "username")


# ---------------------------------------------------------------------------
# event_schemas
# ---------------------------------------------------------------------------

def test_update_event():
    print("\n[UpdateEventSchema]")
    s = UpdateEventSchema()

    assert_valid(s, {"title": "Battle of Helm's Deep"}, "valid title update")
    assert_valid(s, {"year": 3019, "era": "TA"}, "valid year+era update")
    assert_valid(s, {
        "characters": ["char-1", "char-2"],
        "locations": ["loc-1"]
    }, "valid character/location IDs")

    # Known issue: UpdateEventSchema has no validates_schema for empty check,
    # unlike all other Update schemas. Empty payload currently passes.
    try:
        s.load({})
        fail("empty payload accepted — UpdateEventSchema missing validates_schema (known issue)")
    except ValidationError:
        ok("empty payload correctly rejected")

    assert_invalid(s, {"story_position": -1}, "negative story_position rejected", "story_position")


def test_add_event_connection():
    print("\n[AddEventConnectionSchema]")
    s = AddEventConnectionSchema()

    assert_valid(s, {"target_event_id": "evt-456"}, "valid minimal connection")
    assert_valid(s, {
        "target_event_id": "evt-456",
        "relation_type": "causation",
        "relation_label": "directly caused"
    }, "valid full connection")

    assert_invalid(s, {}, "missing 'target_event_id'", "target_event_id")
    assert_invalid(s, {
        "target_event_id": "evt-456",
        "relation_type": "random"       # ← not in OneOf
    }, "invalid relation_type rejected", "relation_type")


# ---------------------------------------------------------------------------
# gpt_schemas
# ---------------------------------------------------------------------------

def test_gpt_paraphrase():
    print("\n[GptParaphraseSchema]")
    s = GptParaphraseSchema()

    assert_valid(s, {"text": "Once upon a time..."}, "valid text")
    assert_valid(s, {"text": "Expand this.", "mode": "expand"}, "valid expand mode")
    assert_invalid(s, {}, "missing required 'text'", "text")
    assert_invalid(s, {"text": ""}, "empty text rejected", "text")
    assert_invalid(s, {
        "text": "A" * 5001             # ← exceeds max 5000
    }, "text > 5000 chars rejected", "text")
    assert_invalid(s, {
        "text": "Some text",
        "mode": "rewrite"              # ← not in OneOf
    }, "invalid mode rejected", "mode")


# ---------------------------------------------------------------------------
# admin_schemas
# ---------------------------------------------------------------------------

def test_change_user_role():
    print("\n[ChangeUserRoleSchema]")
    s = ChangeUserRoleSchema()

    for role in ['admin', 'moderator', 'premium', 'user', 'guest']:
        assert_valid(s, {"role": role}, f"valid role '{role}'")

    assert_invalid(s, {}, "missing 'role'", "role")
    assert_invalid(s, {"role": "superuser"}, "invalid role 'superuser' rejected", "role")


def test_ban_user():
    print("\n[BanUserSchema]")
    s = BanUserSchema()

    assert_valid(s, {}, "empty payload — defaults to banned=True")
    assert_valid(s, {"banned": False, "reason": "Appeal accepted"}, "unban with reason")
    assert_invalid(s, {
        "reason": "A" * 501            # ← exceeds max 500
    }, "reason > 500 chars rejected", "reason")


def test_list_users_query():
    print("\n[ListUsersQuerySchema]")
    s = ListUsersQuerySchema()

    assert_valid(s, {}, "empty params — all defaults")
    assert_valid(s, {"role": "premium", "search": "john"}, "valid role filter")
    assert_invalid(s, {"role": "superuser"}, "invalid role rejected", "role")
    assert_invalid(s, {"per_page": "200"}, "per_page > 100 rejected", "per_page")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all():
    tests = [
        # world
        test_create_world,
        test_update_world,
        test_list_worlds_query,
        test_create_entity,
        test_update_entity,
        test_add_collaborator,
        test_reorder_chapters,
        # story
        test_create_story,
        test_update_story,
        test_list_stories_query,
        test_link_entities,
        test_add_story_event,
        # auth
        test_register,
        test_login,
        test_google_auth,
        test_change_password,
        test_update_profile,
        # event
        test_update_event,
        test_add_event_connection,
        # gpt
        test_gpt_paraphrase,
        # admin
        test_change_user_role,
        test_ban_user,
        test_list_users_query,
    ]

    for t in tests:
        print(f"\n{'='*55}")
        print(f"  {t.__name__}")
        print('='*55)
        try:
            t()
        except Exception as e:
            fail(f"Unexpected exception in {t.__name__}: {e}")

    print(f"\n{'='*55}")
    print(f"  Results: {PASS} passed, {FAIL} failed")
    print('='*55)

    if FAIL:
        sys.exit(1)


if __name__ == '__main__':
    run_all()
