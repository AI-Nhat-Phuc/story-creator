# DESIGN — backend security hardening

> **Status**: DRAFT
> **Phase**: DESIGN
> **Date**: 2026-04-11

The DESIGN phase only permits edits to `api/schemas/` and `api/core/models/`.
All service/route/middleware edits are deferred to IMPLEMENT and are listed
below under "Deferred to IMPLEMENT" so the full shape is reviewable.

---

## Changed Files (DESIGN phase)

| File | Change Type | Maps to Spec Clause |
|------|-------------|---------------------|
| `api/schemas/gpt_schemas.py` | MODIFY — add `GenerateDescriptionSchema`, `GptAnalyzeSchema`, `_sanitize_prompt_text` helper | SUB-3 Behavior, Business Rule 6, Edge Cases SUB-3 |
| `api/core/models/user.py` | MODIFY — filter `to_safe_dict()` metadata via `_SAFE_METADATA_KEYS` whitelist | SUB-5 Behavior, Business Rule 10, Edge Case "User with `metadata.banned = True` fetches own profile" |

No model class signatures change. No schema class is removed. `GptParaphraseSchema` is unchanged (the paraphrase endpoint already uses it).

---

## Schema / Interface Changes

### `api/schemas/gpt_schemas.py`

New private helper (module-level):

```python
_PROMPT_INJECTION_MARKERS = (
    'system:',
    'assistant:',
    '<|im_start|>',
    '<|im_end|>',
    '```',
)

def _sanitize_prompt_text(value):
    """Case-insensitive strip of prompt-injection markers. Non-string -> untouched."""
```

- Case-insensitive scan via `str.lower().find(marker)`.
- Returns the value as-is for non-string inputs (Marshmallow field validators already enforce types).
- Applied inside each schema's `@post_load` hook, not inside individual field validators — this keeps validation errors about length separate from sanitization.

New schema — maps to spec SUB-3 `POST /api/gpt/generate-description`:

```python
class GenerateDescriptionSchema(Schema):
    type              = fields.Str(required=True,
                                    validate=OneOf(['world', 'story']))

    # World variant
    world_name        = fields.Str(load_default='', validate=Length(max=200))
    world_type        = fields.Str(load_default='fantasy', validate=Length(max=50))

    # Story variant
    story_title       = fields.Str(load_default='', validate=Length(max=200))
    story_genre       = fields.Str(load_default='adventure', validate=Length(max=50))
    world_description = fields.Str(load_default='', validate=Length(max=5000))
    characters        = fields.Str(load_default='', validate=Length(max=1000))

    @post_load
    def _sanitize(self, data, **_): ...
```

Rationale for `load_default=''` (not `required=True`): the current route accepts the world or story variant and checks the variant-specific field in Python. Keeping the route logic untouched (a non-breaking design goal) means the schema must accept partial payloads. Required-ness of `world_name` vs `story_title` is enforced by the route after `type` dispatch.

New schema — maps to spec SUB-3 `POST /api/gpt/analyze`:

```python
class GptAnalyzeSchema(Schema):
    world_description = fields.Str(load_default='', validate=Length(max=10000))
    story_content     = fields.Str(load_default='', validate=Length(max=10000))
    world_name        = fields.Str(load_default='', validate=Length(max=200))
    story_title       = fields.Str(load_default='', validate=Length(max=200))

    @post_load
    def _sanitize(self, data, **_): ...
```

Same partial-payload rationale — the `/analyze` route dispatches on whichever field is populated.

### What these schemas do NOT do

- They do not dispatch between world/story variants. That remains in the route.
- They do not enforce "at least one of `world_description` or `story_content`". That remains in the route.
- They do not call GPT. They only validate, length-bound, and sanitize.

---

## Model Changes

### `api/core/models/user.py`

New class-level constant:

```python
_SAFE_METADATA_KEYS = (
    'oauth_accounts',
    'public_worlds_limit',
    'public_worlds_count',
    'public_stories_limit',
    'public_stories_count',
    'gpt_requests_per_day',
    'gpt_requests_today',
    'gpt_last_reset',
)
```

Modified method:

```python
def to_safe_dict(self) -> Dict[str, Any]:
    safe_metadata = {
        k: self.metadata[k]
        for k in self._SAFE_METADATA_KEYS
        if k in self.metadata
    }
    return {
        'user_id':    self.user_id,
        'username':   self.username,
        'email':      self.email,
        'role':       self.role,
        'created_at': self.created_at,
        'metadata':   safe_metadata,
    }
```

Behavioral delta:
- Previously: `metadata` field returned verbatim, including `banned`, `ban_reason`, `banned_by`, and any ad-hoc keys set elsewhere.
- Now: returns only the whitelist. Any key not in `_SAFE_METADATA_KEYS` is absent from the dict.

Non-breaking evidence gathered during ANALYZE:
- Frontend `AdminPanel.jsx` and `AuthContext.jsx` do not read `metadata.banned`, `metadata.ban_reason`, or `metadata.banned_by` from `to_safe_dict()` responses (confirmed by the user in pre-flight check #2).
- Frontend Dashboard reads `user.metadata.public_worlds_count`, `public_worlds_limit`, `public_stories_count`, `public_stories_limit`, `gpt_requests_per_day` — all of which remain in `_SAFE_METADATA_KEYS`.
- Admin-only moderation endpoints (`admin_routes.py`) access `User.metadata` directly via `to_dict()` or database reads, not through `to_safe_dict()`. They are unaffected.

`to_dict()` is unchanged — it still returns the full metadata dict for internal/admin use.

---

## New Method Signatures

No new public methods on `User`. The sanitizer is a private module-level helper, not a method.

---

## Deferred to IMPLEMENT (for review completeness — not edited in this phase)

These are the edits that will happen in IMPLEMENT, listed here so reviewers can cross-check against the spec without having to re-derive them. Each is blocked by SDD hook during DESIGN.

| File | Change | Spec clause |
|------|--------|-------------|
| `api/services/auth_service.py` | Remove `'dev-secret-key-change-in-production'` fallback; raise `RuntimeError` when `JWT_SECRET_KEY` missing and `FLASK_ENV != 'development'`; generate random per-process key in dev and log warning | SUB-1 Behavior, Business Rule 1, Edge Cases SUB-1 |
| `api/interfaces/routes/auth_routes.py` | Add Google tokeninfo audience verify; reduce auth limiter from `30 per minute` to `10 per minute` | SUB-1 Behavior, SUB-5 Behavior, Business Rules 2, 8 |
| `api/interfaces/routes/event_routes.py` | Add `@token_required` to `/extract` and `/cache` and `/events/<id>` DELETE routes | SUB-2 Behavior, Business Rule 5 |
| `api/interfaces/routes/gpt_routes.py` | Apply `@validate_request(GenerateDescriptionSchema)` and `@validate_request(GptAnalyzeSchema)`; read from `request.validated_data`; swap `print` → `logger.debug`; generic error message for `ExternalServiceError('GPT', ...)`; add `@_gpt_limit` to `gpt_get_results` | SUB-3, SUB-4, SUB-5 |
| `api/interfaces/api_backend.py` | Gate admin seed behind `INITIAL_ADMIN_PASSWORD` env var; gate test seed behind `SEED_TEST_USER=1`; add `after_request` hook for security headers; regex-validate `VERCEL_URL` | SUB-2, SUB-4 |
| `api/storage/mongo_storage.py` | Replace `getattr(self, collection_name)` with explicit whitelist dict | SUB-5 Business Rule 9 |
| `api/test_security.py` | New test file — regression coverage for all SUBs | SUB-6 |

These files are **not** touched in DESIGN — the SDD hook will block any attempt. This list is for reviewer orientation only.

---

## Risk & Rollback

### Schemas (SUB-3)
- **Risk**: Existing GPT world/story creation requests with `world_name > 200 chars` start failing with 400.
- **Mitigation**: 200 chars is a generous upper bound for any legitimate world/story title. If a real user exceeds it, we hear about it via a 400 and can relax the bound in a follow-up without migration.
- **Rollback**: Reverting the diff on `gpt_schemas.py` restores prior permissive behavior. The route still reads from `request.json` as a fallback until IMPLEMENT wires in `@validate_request`, so schema changes are dormant until then.

### User model (SUB-5)
- **Risk**: A yet-unseen frontend code path reads a metadata key we filtered out.
- **Mitigation**: Whitelist includes every metadata key the model constructor initializes in `_init_role_quotas()` plus `oauth_accounts` (set by OAuth flow). The only fields actively filtered are moderation-related, confirmed unused by pre-flight check #2.
- **Rollback**: Revert the `to_safe_dict` diff — single-method change, trivial to revert.

### DESIGN-phase changes are dormant

A critical property of this design: both edits are **inactive until IMPLEMENT wires them in**. The new schemas are not referenced by any route yet, and `to_safe_dict` change is live but already verified safe against frontend usage. If CI runs against this branch as-is, existing tests must still pass because:

1. New schemas live alongside `GptParaphraseSchema` but are only instantiated by code that doesn't exist yet.
2. `to_safe_dict` filtering only removes keys the frontend confirmed unused.

---

## Cross-reference: Spec clause → DESIGN artifact

| Spec clause | Covered by |
|-------------|-----------|
| SUB-1 JWT fail-fast | *(deferred — service-layer)* |
| SUB-1 Google `aud` verify | *(deferred — route-layer)* |
| SUB-2 Event route auth | *(deferred — route-layer)* |
| SUB-2 Admin seed gating | *(deferred — backend init)* |
| SUB-2 Test seed gating | *(deferred — backend init)* |
| SUB-3 `GenerateDescriptionSchema` | **`gpt_schemas.py` new schema** |
| SUB-3 `GptAnalyzeSchema` | **`gpt_schemas.py` new schema** |
| SUB-3 Prompt injection sanitizer | **`gpt_schemas.py` `_sanitize_prompt_text`** |
| SUB-3 `print` → `logger.debug` | *(deferred — route-layer)* |
| SUB-4 Error message sanitization | *(deferred — route-layer)* |
| SUB-4 Security headers | *(deferred — backend init)* |
| SUB-4 CORS regex validation | *(deferred — backend init)* |
| SUB-5 Auth rate limit 10/min | *(deferred — route-layer)* |
| SUB-5 GPT results rate limit | *(deferred — route-layer)* |
| SUB-5 Collection whitelist | *(deferred — storage-layer)* |
| SUB-5 `to_safe_dict` metadata filter | **`user.py` `_SAFE_METADATA_KEYS` + method** |
| SUB-6 Regression tests | *(deferred — IMPLEMENT)* |
