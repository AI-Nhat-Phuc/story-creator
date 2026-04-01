"""Validation schemas for GPT-related endpoints."""

from marshmallow import Schema, fields, validate


class GptParaphraseSchema(Schema):
    """Schema for POST /api/gpt/paraphrase — SUB-3 Story Editor."""

    text = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=5000),
        error_messages={'required': 'Text to paraphrase is required'}
    )

    mode = fields.Str(
        validate=validate.OneOf(['paraphrase', 'expand']),
        load_default='paraphrase'
    )
