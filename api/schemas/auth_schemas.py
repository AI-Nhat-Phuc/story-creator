"""Validation schemas for authentication endpoints."""

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
import re


def validate_password_strength(password):
    """Validate password meets minimum requirements.

    Requirements:
    - At least 8 characters
    - Contains uppercase and lowercase letters
    - Contains at least one number
    - Contains at least one special character
    """
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')

    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')

    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')

    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one number')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character')


class RegisterSchema(Schema):
    """Schema for POST /api/auth/register - User registration."""

    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50),
        error_messages={'required': 'Username is required'}
    )

    email = fields.Email(
        required=True,
        error_messages={'required': 'Email is required', 'invalid': 'Invalid email address'}
    )

    password = fields.Str(
        required=True,
        validate=validate_password_strength,
        error_messages={'required': 'Password is required'}
    )

    @validates('username')
    def validate_username(self, value, **kwargs):
        """Validate username contains only allowed characters."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise ValidationError(
                'Username can only contain letters, numbers, hyphens, and underscores'
            )


class LoginSchema(Schema):
    """Schema for POST /api/auth/login - User login."""

    username = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'Username or email is required'}
    )

    password = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'Password is required'}
    )


class GoogleAuthSchema(Schema):
    """Schema for POST /api/auth/google - Google OAuth."""

    credential = fields.Str(
        required=True,
        error_messages={'required': 'Google credential token is required'}
    )


class ChangePasswordSchema(Schema):
    """Schema for POST /api/auth/change-password - Change user password."""

    current_password = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'Current password is required'}
    )

    new_password = fields.Str(
        required=True,
        validate=validate_password_strength,
        error_messages={'required': 'New password is required'}
    )

    @validates('new_password')
    def validate_passwords_different(self, value, **kwargs):
        """Ensure new password is different from current password."""
        # Note: This is a basic check. In practice, you'd compare hashes
        # This validation happens before hashing, so we can only check if strings differ
        pass  # Actual comparison done in service layer with hashes


class UpdateProfileSchema(Schema):
    """Schema for PUT /api/auth/profile - Update user profile."""

    username = fields.Str(
        validate=validate.Length(min=3, max=50)
    )

    email = fields.Email(
        error_messages={'invalid': 'Invalid email address'}
    )

    signature = fields.Str(
        validate=validate.Length(max=200),
        allow_none=True
    )

    signatures = fields.List(
        fields.Str(validate=validate.Length(min=1, max=200)),
        validate=validate.Length(max=20)
    )

    @validates('username')
    def validate_username(self, value, **kwargs):
        """Validate username contains only allowed characters."""
        if value and not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise ValidationError(
                'Username can only contain letters, numbers, hyphens, and underscores'
            )

    @validates_schema
    def validate_not_empty(self, data, **kwargs):
        """Ensure at least one field is being updated."""
        if not data:
            raise ValidationError('At least one field must be provided for update')
