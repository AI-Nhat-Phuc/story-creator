"""Validation schemas for story-related endpoints."""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class CreateStorySchema(Schema):
    """Schema for POST /api/stories - Create new story."""

    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Story title is required'}
    )

    world_id = fields.Str(
        required=True,
        error_messages={'required': 'World ID is required'}
    )

    genre = fields.Str(
        validate=validate.Length(max=50),
        load_default='general'
    )

    description = fields.Str(
        validate=validate.Length(max=2000),
        load_default=''
    )

    content = fields.Str(
        validate=validate.Length(max=100000),
        load_default=''
    )

    visibility = fields.Str(
        validate=validate.OneOf(['draft', 'private', 'public']),
        load_default='private'
    )

    tags = fields.List(
        fields.Str(validate=validate.Length(max=50)),
        load_default=list
    )

    # Sort key for novel reading. None → backend auto-assigns max(order)+1.
    order = fields.Int(
        validate=validate.Range(min=1),
        load_default=None,
        allow_none=True
    )

    selected_characters = fields.List(
        fields.Str(),
        load_default=None,
        allow_none=True
    )

    format = fields.Str(
        validate=validate.OneOf(['plain', 'markdown', 'html']),
        load_default='plain'
    )

    use_gpt = fields.Bool(load_default=False)

    gpt_result = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),
        load_default=None,
        allow_none=True
    )


class UpdateStorySchema(Schema):
    """Schema for PUT /api/stories/<id> - Update story."""

    title = fields.Str(
        validate=validate.Length(min=1, max=200)
    )

    description = fields.Str(
        validate=validate.Length(max=2000)
    )

    genre = fields.Str(
        validate=validate.Length(max=50)
    )

    visibility = fields.Str(
        validate=validate.OneOf(['draft', 'private', 'public'])
    )

    tags = fields.List(
        fields.Str(validate=validate.Length(max=50))
    )

    content = fields.Str()

    chapter_number = fields.Int(
        validate=validate.Range(min=1)
    )

    format = fields.Str(
        validate=validate.OneOf(['plain', 'markdown', 'html'])
    )

    # Sort key for novel reading.
    order = fields.Int(
        validate=validate.Range(min=1)
    )

    @validates_schema
    def validate_not_empty(self, data, **kwargs):
        """Ensure at least one field is being updated."""
        if not data:
            raise ValidationError('At least one field must be provided for update')


class ListStoriesQuerySchema(Schema):
    """Schema for GET /api/stories - List stories with filters."""

    page = fields.Int(
        validate=validate.Range(min=1),
        load_default=1
    )

    per_page = fields.Int(
        validate=validate.Range(min=1, max=100),
        load_default=20
    )

    world_id = fields.Str(
        validate=validate.Length(max=100),
        load_default=None,
        allow_none=True
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

    genre = fields.Str(
        validate=validate.Length(max=50),
        load_default=None,
        allow_none=True
    )


class LinkEntitiesSchema(Schema):
    """Schema for POST /api/stories/<id>/link-entities."""

    characters = fields.List(fields.Raw(), load_default=list)
    locations = fields.List(fields.Raw(), load_default=list)
    auto_create = fields.Bool(load_default=True)


class AddStoryEventSchema(Schema):
    """Schema for POST /api/stories/<id>/events - Add event to story."""

    event_type = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'Event type is required'}
    )

    description = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=2000),
        error_messages={'required': 'Event description is required'}
    )

    timestamp = fields.Int(
        validate=validate.Range(min=0),
        load_default=None,
        allow_none=True
    )

    participants = fields.List(
        fields.Str(),
        load_default=list
    )

    location_id = fields.Str(
        validate=validate.Length(max=100),
        load_default=None,
        allow_none=True
    )

    metadata = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),
        load_default=dict
    )
