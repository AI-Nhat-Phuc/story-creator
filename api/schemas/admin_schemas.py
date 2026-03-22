"""Validation schemas for admin endpoints."""

from marshmallow import Schema, fields, validate


class ChangeUserRoleSchema(Schema):
    """Schema for PUT /api/admin/users/<id>/role - Change user role."""

    role = fields.Str(
        required=True,
        validate=validate.OneOf(['admin', 'moderator', 'premium', 'user', 'guest']),
        error_messages={'required': 'role is required'}
    )


class BanUserSchema(Schema):
    """Schema for POST /api/admin/users/<id>/ban - Ban/unban a user."""

    banned = fields.Bool(load_default=True)
    reason = fields.Str(validate=validate.Length(max=500), load_default='')


class ListUsersQuerySchema(Schema):
    """Schema for GET /api/admin/users - List users with pagination."""

    page = fields.Int(validate=validate.Range(min=1), load_default=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), load_default=20)
    role = fields.Str(
        validate=validate.OneOf(['admin', 'moderator', 'premium', 'user', 'guest']),
        load_default=None,
        allow_none=True
    )
    search = fields.Str(validate=validate.Length(max=100), load_default='')
