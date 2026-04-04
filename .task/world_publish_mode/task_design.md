# DESIGN — world publish mode

> **Status**: DRAFT
> **Phase**: DESIGN
> **Date**: 2026-04-03

---

## Changed Files

| File | Change Type | Maps to Spec Clause |
| ---- | ----------- | ------------------- |
| `api/schemas/world_schemas.py` | MODIFY | "Default khi tạo: draft" |

## Schema / Interface Changes

```python
# api/schemas/world_schemas.py — CreateWorldSchema
# BEFORE:
visibility = fields.Str(
    validate=validate.OneOf(['draft', 'private', 'public']),
    load_default='private'
)

# AFTER:
visibility = fields.Str(
    validate=validate.OneOf(['draft', 'private', 'public']),
    load_default='draft'
)
```

## Model Changes

None — `api/core/models/world.py` already accepts `draft` as a visibility value.

## Frontend Changes (IMPLEMENT phase)

| File | Change |
| ---- | ------ |
| `frontend/src/pages/WorldsPage.jsx` | Remove visibility dropdown + quota display from create form |
| `frontend/src/components/worldDetail/WorldDetailView.jsx` | Add Publish button (owner only, hidden when `public`) |
| `frontend/src/containers/WorldDetailContainer.jsx` | Init edit form default to `'draft'` |
