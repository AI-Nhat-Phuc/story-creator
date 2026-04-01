# DESIGN — Collaborative Novel Writing for Two Novelists

> **Status**: DRAFT
> **Phase**: DESIGN
> **Date**: 2026-03-30

---

## Changed Files

| File | Change Type | Maps to Spec Clause |
|------|-------------|---------------------|
| `api/core/models/story.py` | MODIFY | BR-1.2, BR-4.2, BR-4.3 |
| `api/core/models/world.py` | MODIFY | BR-2.1, BR-2.3, BR-4.1 |
| `api/core/models/invitation.py` | NEW | BR-2.1, BR-2.4, EC-2.3 |
| `api/schemas/story_schemas.py` | MODIFY | BR-1.1, BR-4.2 |
| `api/schemas/world_schemas.py` | MODIFY | BR-2.1, BR-2.2 |
| `api/schemas/gpt_schemas.py` | NEW | BR-3.3, BR-3.4 |

---

## Model Changes

### `api/core/models/story.py` — MODIFY

Add two fields to `Story.__init__()` and `to_dict()` / `from_dict()`:

```python
# New fields in __init__
self.updated_at: Optional[str] = updated_at or datetime.now().isoformat()   # BR-1.2 — auto-save timestamp
self.chapter_number: Optional[int] = chapter_number or None                 # BR-4.2 — novel chapter ordering
```

`__init__` signature change:
```python
def __init__(
    self,
    title: str,
    content: str,
    world_id: str,
    story_id: Optional[str] = None,
    created_at: Optional[str] = None,
    updated_at: Optional[str] = None,          # NEW — SUB-1
    chapter_number: Optional[int] = None,       # NEW — SUB-4
    metadata: Optional[Dict[str, Any]] = None,
    visibility: str = 'private',
    owner_id: Optional[str] = None,
    shared_with: Optional[List[str]] = None
):
```

`to_dict()` additions:
```python
"updated_at": self.updated_at,
"chapter_number": self.chapter_number,
```

`from_dict()` additions:
```python
updated_at=data.get("updated_at"),
chapter_number=data.get("chapter_number"),
```

---

### `api/core/models/world.py` — MODIFY

Add two fields to `World.__init__()`:

```python
self.co_authors: List[str] = co_authors or []          # BR-2.1 — list of user_ids with co_author role
self.novel: Optional[Dict[str, Any]] = novel or None   # BR-4.1 — novel metadata block
```

Novel metadata structure (stored as dict in `world.novel`):
```python
{
    "title": str,           # defaults to world name
    "description": str,     # cover description
    "chapter_order": []     # ordered list of story_ids — BR-4.2
}
```

`__init__` signature change:
```python
def __init__(
    self,
    name: str,
    description: str,
    world_id: Optional[str] = None,
    created_at: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    visibility: str = 'private',
    owner_id: Optional[str] = None,
    shared_with: Optional[List[str]] = None,
    co_authors: Optional[List[str]] = None,         # NEW — SUB-2
    novel: Optional[Dict[str, Any]] = None           # NEW — SUB-4
):
```

`to_dict()` additions:
```python
"co_authors": self.co_authors,
"novel": self.novel,
```

`from_dict()` additions:
```python
co_authors=data.get("co_authors", []),
novel=data.get("novel"),
```

---

### `api/core/models/invitation.py` — NEW

New model for co-author invitations (SUB-2):

```python
class Invitation:
    def __init__(
        self,
        world_id: str,
        invited_by: str,       # owner user_id
        invitee_id: str,       # target user_id
        invitation_id: Optional[str] = None,
        status: str = 'pending',   # pending | accepted | declined
        created_at: Optional[str] = None
    ):
        self.invitation_id = invitation_id or str(uuid.uuid4())
        self.world_id = world_id
        self.invited_by = invited_by
        self.invitee_id = invitee_id
        self.status = status   # EC-2.3: invalidated when world deleted
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]: ...
    def from_dict(cls, data) -> 'Invitation': ...
```

---

## Schema Changes

### `api/schemas/story_schemas.py` — MODIFY

**`UpdateStorySchema`** — add two optional fields:

```python
content = fields.Str(
    load_default=None,
    allow_none=True       # SUB-1: auto-save sends only content
)

chapter_number = fields.Int(
    validate=validate.Range(min=1),
    load_default=None,
    allow_none=True       # SUB-4: assign story to chapter slot
)
```

---

### `api/schemas/world_schemas.py` — MODIFY

**New schemas** appended to the file:

```python
class AddCollaboratorSchema(Schema):
    """Schema for POST /api/worlds/{world_id}/collaborators — SUB-2."""
    username_or_email = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    role = fields.Str(
        validate=validate.OneOf(['co_author']),
        load_default='co_author'
    )

class UpdateNovelSchema(Schema):
    """Schema for PUT /api/worlds/{world_id}/novel — SUB-4."""
    title = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str(validate=validate.Length(max=2000))

    @validates_schema
    def validate_not_empty(self, data, **kwargs):
        if not data:
            raise ValidationError('At least one field must be provided')

class ReorderChaptersSchema(Schema):
    """Schema for PATCH /api/worlds/{world_id}/novel/chapters — SUB-4."""
    order = fields.List(
        fields.Str(),
        required=True,
        validate=validate.Length(min=0)
    )
```

---

### `api/schemas/gpt_schemas.py` — NEW

```python
class GptParaphraseSchema(Schema):
    """Schema for POST /api/gpt/paraphrase — SUB-3."""
    text = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=5000)
    )
    mode = fields.Str(
        validate=validate.OneOf(['paraphrase', 'expand']),
        load_default='paraphrase'
    )
```

---

## Summary of All New Endpoints

| Endpoint | Schema | Spec Clause |
|----------|--------|-------------|
| `POST /api/worlds/{id}/collaborators` | `AddCollaboratorSchema` | SUB-2 BR-2.1 |
| `GET /api/worlds/{id}/collaborators` | — | SUB-2 BR-2.1 |
| `DELETE /api/worlds/{id}/collaborators/{user_id}` | — | SUB-2 BR-2.1 |
| `GET /api/users/me/invitations` | — | SUB-2 BR-2.4 |
| `POST /api/users/me/invitations/{id}/accept` | — | SUB-2 BR-2.5 |
| `POST /api/users/me/invitations/{id}/decline` | — | SUB-2 BR-2.5 |
| `GET /api/worlds/{id}/novel` | — | SUB-4 BR-4.1 |
| `PUT /api/worlds/{id}/novel` | `UpdateNovelSchema` | SUB-4 BR-4.1 |
| `PATCH /api/worlds/{id}/novel/chapters` | `ReorderChaptersSchema` | SUB-4 BR-4.2 |
| `POST /api/gpt/paraphrase` | `GptParaphraseSchema` | SUB-3 BR-3.3 |
