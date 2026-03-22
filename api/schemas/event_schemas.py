"""Validation schemas for event-related endpoints."""

from marshmallow import Schema, fields, validate


class UpdateEventSchema(Schema):
    """Schema for PUT /api/events/<id> - Update an event."""

    title = fields.Str(validate=validate.Length(max=200))
    description = fields.Str(validate=validate.Length(max=2000))
    year = fields.Int()
    era = fields.Str(validate=validate.Length(max=50))
    story_position = fields.Int(validate=validate.Range(min=0))
    characters = fields.List(fields.Raw())
    locations = fields.List(fields.Raw())
    connections = fields.List(fields.Raw())
    metadata = fields.Dict(keys=fields.Str(), values=fields.Raw())


class AddEventConnectionSchema(Schema):
    """Schema for POST /api/events/<id>/connections - Add a connection between events."""

    target_event_id = fields.Str(
        required=True,
        error_messages={'required': 'target_event_id is required'}
    )
    relation_type = fields.Str(
        validate=validate.OneOf(['character', 'location', 'causation', 'temporal']),
        load_default='temporal'
    )
    relation_label = fields.Str(validate=validate.Length(max=200), load_default='')
