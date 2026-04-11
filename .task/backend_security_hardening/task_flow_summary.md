# Flow Summary — backend security hardening

> **Status**: PENDING
> **File**: `api/interfaces/routes/event_routes.py`
> **Date**: 2026-04-11
> **SUB**: 2 (event route authorization)

---

## Current Flow

### `create_event_bp(storage, gpt_results, backend)`

Creates blueprint with 7 routes:

| Route | Method | Auth | Notes |
|---|---|---|---|
| `/api/worlds/<world_id>/events` | GET | none | read-only timeline |
| `/api/worlds/<world_id>/events/extract` | POST | **none** | triggers GPT |
| `/api/stories/<story_id>/events/extract` | POST | **none** | triggers GPT |
| `/api/stories/<story_id>/events/cache` | DELETE | **none** | clears cache |
| `/api/events/<event_id>` | PUT | `@token_required` | already protected |
| `/api/events/<event_id>` | DELETE | **none** | destructive |
| `/api/events/<event_id>/connections` | POST | `@token_required` | already protected |

### Observed Issues

- **Issue A (SUB-2)**: Four routes are anonymous:
  1. `extract_world_events` (line 55) — triggers GPT analysis over every story in a world. Anonymous GPT cost amplification.
  2. `extract_story_events` (line 118) — same, single story.
  3. `clear_story_event_cache` (line 176) — destructive (wipes analysis cache). No auth.
  4. `delete_event` (line 252) — destructive (removes event row). No auth.
- **Issue B (non-breaking check)**: Frontend axios interceptor auto-attaches `Authorization: Bearer <jwt>` when logged in. So adding `@token_required` is transparent for logged-in users; anonymous callers (none in practice) get 401. Verified earlier during ANALYZE phase.
- **Issue C (out of scope)**: `PermissionService.can_edit(user, world)` could be checked on destructive routes for stricter per-resource authz, but spec only requires `@token_required` — any logged-in user passes. Ownership enforcement is a follow-up.

### Unchanged behavior

- `get_world_timeline` stays anonymous (public read — spec §SUB-2: "`GET /api/worlds/<world_id>/events` remains publicly readable for public worlds").
- `update_event` and `add_event_connection` already have `@token_required` — unchanged.

---

## Planned Changes

Add `@token_required` decorator to exactly four route functions. The decorator is already imported at line 11 (`from interfaces.auth_middleware import token_required`) — no import changes needed.

### Change 1 — `extract_world_events` (line 54)

```python
@event_bp.route('/api/worlds/<world_id>/events/extract', methods=['POST'])
@token_required
def extract_world_events(world_id):
```

### Change 2 — `extract_story_events` (line 117)

```python
@event_bp.route('/api/stories/<story_id>/events/extract', methods=['POST'])
@token_required
def extract_story_events(story_id):
```

### Change 3 — `clear_story_event_cache` (line 175)

```python
@event_bp.route('/api/stories/<story_id>/events/cache', methods=['DELETE'])
@token_required
def clear_story_event_cache(story_id):
```

### Change 4 — `delete_event` (line 251)

```python
@event_bp.route('/api/events/<event_id>', methods=['DELETE'])
@token_required
def delete_event(event_id):
```

### NOT changing

- Route bodies (all business logic preserved verbatim).
- `get_world_timeline` (stays anonymous).
- `update_event`, `add_event_connection` (already protected).
- No new imports, no new helpers, no error-handling changes.

---

## Backward Compatibility

- Frontend: axios request interceptor in `frontend/src/services/api.js` adds `Authorization: Bearer <token>` to every API call when a token exists in `AuthContext`. All callers of these routes from the React UI already run behind `ProtectedRoute`, so the token is always present at call time. Zero frontend code change.
- Anonymous callers (curl, Postman, third-party scripts): now receive 401. Acceptable — these endpoints trigger paid GPT work and are not part of any public API contract.
- Existing logged-in sessions: unaffected. The JWT is already being sent; the new decorator just validates and populates `g.current_user`.

---

## Test coverage wired

- `TestEventRouteAuth.test_extract_world_events_requires_auth` → will pass
- `TestEventRouteAuth.test_extract_story_events_requires_auth` → will pass
- `TestEventRouteAuth.test_clear_story_event_cache_requires_auth` → will pass
- `TestEventRouteAuth.test_delete_event_requires_auth` → will pass
- `TestEventRouteAuth.test_get_world_events_still_public` → should stay green (already green)
