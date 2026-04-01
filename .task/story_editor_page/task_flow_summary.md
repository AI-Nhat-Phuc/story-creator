# Flow Summary — Story Editor Page

---

## File 1: api/interfaces/routes/story_routes.py

### Current input/output
- `POST /api/stories` — creates story from validated data, returns `{story_id, story, time_cone}`
- `GET /api/stories/<story_id>` — returns story dict
- `PUT /api/stories/<story_id>` — updates story fields, returns story dict

### Execution steps (create_story)
1. `@validate_request(CreateStorySchema)` populates `request.validated_data`
2. Load world, check `can_view` permission
3. If `visibility='public'` → check public story quota
4. `story_generator.generate(title, description, world_id, genre, …)`
5. Set `story.owner_id`, `story.visibility`
6. `_set_world_time(story, world, time_index)`
7. `story_generator.generate_time_cone(…)`
8. `storage.save_story / save_time_cone / save_world`
9. If public → `user.increment_public_stories()`
10. Return `created_response({story_id, story, time_cone})`

### Observed issues (NOT fixing unless listed below)
- `format` from `CreateStorySchema` never applied to `story.format`
- No one-draft enforcement in `create_story` or `update_story`
- `update_story` does not update `format` field
- `GET /api/stories/<story_id>` captures literal `my-draft` as a param → 404 instead of 401

### Exact planned changes

**1. Add `GET /api/stories/my-draft` BEFORE `GET /api/stories/<story_id>`**
- `@token_required`
- Query: `storage.list_stories(owner_id=user_id, visibility='draft')` → first or None
- Return `success_response({'story': story_data_or_none})`

**2. `create_story`: apply `format` + enforce one-draft rule**
- After setting `story.visibility`, add: `story.format = data.get('format', 'plain')`
- When `visibility == 'draft'`: query existing drafts for user → 409 `ConflictError` if found

**3. `update_story`: enforce draft rule + update `format`**
- When changing TO `draft` (new != old and new == 'draft'):
  check other drafts by user (excluding this story_id) → 409 if found
- Add `'format'` to field-copy loop alongside `'title'`, `'content'`

### Will NOT change
- `patch_story`, `delete_story`, `list_stories`, `story_link_entities`, `story_clear_links`
- Helper functions `_resolve_linked_entities`, `_set_world_time`

---

## File 2: api/interfaces/routes/auth_routes.py

### Current input/output
- No `PUT /api/auth/profile` endpoint exists
- `GET /auth/me` returns `{'success': True, 'user': user.to_safe_dict()}` (no `data` envelope)

### Execution steps (existing pattern for reference)
1. `_get_user_from_auth_header` extracts + validates Bearer token
2. `auth_service.get_user_from_token(token)` → User object
3. Route logic runs, returns `jsonify(...)` or `success_response(...)`

### Observed issues
- `UpdateProfileSchema` exists in `auth_schemas.py` (with `username`, `email`, `signature`) but no route uses it
- `GET /auth/me` uses `jsonify` directly (not `success_response`) — not changing

### Exact planned changes

**Add `PUT /api/auth/profile`**
- `@token_required` (use existing decorator, not `_get_user_from_auth_header`)
- `@validate_request(UpdateProfileSchema)`
- Load raw user dict: `storage.load_user(g.current_user.user_id)`
- Apply fields: `username`, `email` if present; `signature` → `user_data['metadata']['signature']`
- `storage.save_user(user_data)`
- Return `success_response({'user': user_data})`
- Add imports: `UpdateProfileSchema`, `token_required`, `success_response`, `g`

### Will NOT change
- `register`, `login`, `verify_token`, `change_password`, `get_current_user`, `oauth_google`
- `_get_user_from_auth_header` helper
