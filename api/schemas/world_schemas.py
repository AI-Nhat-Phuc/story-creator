"""Validation schemas for world-related endpoints."""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class CreateWorldSchema(Schema):
    """Schema for POST /api/worlds - Create new world."""

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'World name is required'}
    )

    world_type = fields.Str(
        required=True,
        validate=validate.OneOf(['fantasy', 'sci-fi', 'modern', 'historical']),
        error_messages={'required': 'World type is required'}
    )

    description = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=5000),
        error_messages={'required': 'World description is required'}
    )

    visibility = fields.Str(
        validate=validate.OneOf(['draft', 'private', 'public']),
        load_default='draft'
    )

    use_gpt = fields.Bool(load_default=False)

    gpt_entities = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),
        load_default=None,
        allow_none=True
    )


class UpdateWorldSchema(Schema):
    """Schema for PUT /api/worlds/<id> - Update world."""

    name = fields.Str(
        validate=validate.Length(min=1, max=100)
    )

    description = fields.Str(
        validate=validate.Length(min=10, max=5000)
    )

    visibility = fields.Str(
        validate=validate.OneOf(['draft', 'private', 'public'])
    )

    world_type = fields.Str(
        validate=validate.OneOf(['fantasy', 'sci-fi', 'modern', 'historical'])
    )

    @validates_schema
    def validate_not_empty(self, data, **kwargs):
        """Ensure at least one field is being updated."""
        if not data:
            raise ValidationError('At least one field must be provided for update')


class ListWorldsQuerySchema(Schema):
    """Schema for GET /api/worlds - List worlds with pagination."""

    page = fields.Int(
        validate=validate.Range(min=1),
        load_default=1
    )

    per_page = fields.Int(
        validate=validate.Range(min=1, max=100),
        load_default=20
    )

    visibility = fields.Str(
        validate=validate.OneOf(['draft', 'private', 'public', 'all']),
        load_default='all'
    )

    owner_id = fields.Str(
        validate=validate.Length(max=100),
        load_default=None,
        allow_none=True
    )


class ListWorldStoriesQuerySchema(Schema):
    """Schema for GET /api/worlds/<id>/stories — paginated story summaries."""

    page = fields.Int(
        validate=validate.Range(min=1),
        load_default=1
    )

    per_page = fields.Int(
        validate=validate.Range(min=1, max=100),
        load_default=20
    )


class CreateEntitySchema(Schema):
    """Schema for POST /api/worlds/<id>/entities - Add entity to world."""

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'Entity name is required'}
    )

    entity_type = fields.Str(
        required=True,
        validate=validate.OneOf(['character', 'location', 'object', 'concept']),
        error_messages={'required': 'Entity type is required'}
    )

    description = fields.Str(
        validate=validate.Length(max=1000),
        load_default=''
    )

    attributes = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),
        load_default=dict
    )


class UpdateEntitySchema(Schema):
    """Schema for PUT /api/worlds/<world_id>/entities/<entity_id> - Update entity."""

    name = fields.Str(
        validate=validate.Length(min=1, max=100)
    )

    description = fields.Str(
        validate=validate.Length(max=1000)
    )

    attributes = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw()
    )

    @validates_schema
    def validate_not_empty(self, data, **kwargs):
        """Ensure at least one field is being updated."""
        if not data:
            raise ValidationError('At least one field must be provided for update')


class AddCollaboratorSchema(Schema):
    """Schema for POST /api/worlds/{world_id}/collaborators — SUB-2."""

    username_or_email = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Username or email is required'}
    )

    role = fields.Str(
        validate=validate.OneOf(['co_author']),
        load_default='co_author'
    )


class UpdateNovelSchema(Schema):
    """Schema for PUT /api/worlds/{world_id}/novel — SUB-4."""

    title = fields.Str(
        validate=validate.Length(min=1, max=200)
    )

    description = fields.Str(
        validate=validate.Length(max=2000)
    )

    @validates_schema
    def validate_not_empty(self, data, **kwargs):
        if not data:
            raise ValidationError('At least one field must be provided')


class ReorderChaptersSchema(Schema):
    """Schema for PATCH /api/worlds/{world_id}/novel/chapters — SUB-4."""

    order = fields.List(
        fields.Str(),
        required=True,
        error_messages={'required': 'Chapter order list is required'}
    )


class NovelContentQuerySchema(Schema):
    """Query params for GET /api/worlds/{world_id}/novel/content.

    Paginated novel content as a stream of blocks ordered by Story.order ASC.
    Cursor is opaque (server-encoded {order, line offset}).
    """

    cursor = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=200)
    )

    line_budget = fields.Int(
        validate=validate.Range(min=1, max=500),
        load_default=100
    )
