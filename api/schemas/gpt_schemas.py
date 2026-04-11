"""Validation schemas for GPT-related endpoints."""

from marshmallow import Schema, fields, validate, post_load


# Prompt-injection markers stripped from any free-text field before
# the value is formatted into a GPT prompt template. Keep the list
# conservative — only sequences that have no legitimate use inside
# story/world descriptions. See spec SUB-3 Business Rule 6.
_PROMPT_INJECTION_MARKERS = (
    'system:',
    'assistant:',
    '<|im_start|>',
    '<|im_end|>',
    '```',
)


def _sanitize_prompt_text(value):
    """Strip prompt-injection markers from a string (case-insensitive).

    Returns the value unchanged if it is not a string. Non-string inputs
    are handled upstream by Marshmallow field validation.
    """
    if not isinstance(value, str):
        return value
    sanitized = value
    lowered = sanitized.lower()
    for marker in _PROMPT_INJECTION_MARKERS:
        # Case-insensitive replace while preserving other characters.
        idx = lowered.find(marker)
        while idx != -1:
            sanitized = sanitized[:idx] + sanitized[idx + len(marker):]
            lowered = sanitized.lower()
            idx = lowered.find(marker)
    return sanitized


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


class GenerateDescriptionSchema(Schema):
    """Schema for POST /api/gpt/generate-description.

    Covers both `type=world` and `type=story` variants. Fields not
    relevant to the chosen type are simply ignored by the route, but
    all free-text fields are length-bounded and injection-sanitized
    regardless. See spec SUB-3.
    """

    type = fields.Str(
        required=True,
        validate=validate.OneOf(['world', 'story']),
        error_messages={'required': 'type is required'}
    )

    # World variant
    world_name = fields.Str(
        load_default='',
        validate=validate.Length(max=200)
    )
    world_type = fields.Str(
        load_default='fantasy',
        validate=validate.Length(max=50)
    )

    # Story variant
    story_title = fields.Str(
        load_default='',
        validate=validate.Length(max=200)
    )
    story_genre = fields.Str(
        load_default='adventure',
        validate=validate.Length(max=50)
    )
    world_description = fields.Str(
        load_default='',
        validate=validate.Length(max=5000)
    )
    characters = fields.Str(
        load_default='',
        validate=validate.Length(max=1000)
    )

    @post_load
    def _sanitize(self, data, **_kwargs):
        for key in (
            'world_name',
            'world_type',
            'story_title',
            'story_genre',
            'world_description',
            'characters',
        ):
            if key in data:
                data[key] = _sanitize_prompt_text(data[key])
        return data


class GptAnalyzeSchema(Schema):
    """Schema for POST /api/gpt/analyze.

    Accepts either a world description or a story block (under either
    ``story_content`` or ``story_description`` — the route accepts both
    aliases so the schema stays non-breaking for the frontend) for
    entity/location extraction. At least one of the text fields must
    be provided; the existing route logic handles the branching.
    """

    world_description = fields.Str(
        load_default='',
        validate=validate.Length(max=10000)
    )
    story_content = fields.Str(
        load_default='',
        validate=validate.Length(max=10000)
    )
    story_description = fields.Str(
        load_default='',
        validate=validate.Length(max=10000)
    )
    world_name = fields.Str(
        load_default='',
        validate=validate.Length(max=200)
    )
    story_title = fields.Str(
        load_default='',
        validate=validate.Length(max=200)
    )
    story_genre = fields.Str(
        load_default='',
        validate=validate.Length(max=50)
    )
    world_type = fields.Str(
        load_default='',
        validate=validate.Length(max=50)
    )

    @post_load
    def _sanitize(self, data, **_kwargs):
        for key in (
            'world_description',
            'story_content',
            'story_description',
            'world_name',
            'story_title',
            'story_genre',
            'world_type',
        ):
            if key in data:
                data[key] = _sanitize_prompt_text(data[key])
        return data
