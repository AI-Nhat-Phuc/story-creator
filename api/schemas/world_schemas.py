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
        load_default='private'
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
