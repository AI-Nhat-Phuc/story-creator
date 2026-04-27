"""Custom exception hierarchy for API error handling."""


class APIException(Exception):
    """Base exception for all API errors."""

    status_code = 500
    error_code = 'internal_error'

    def __init__(self, message, details=None):
        """Initialize API exception.

        Args:
            message: Human-readable error message
            details: Additional error details (dict)
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(APIException):
    """Request validation failed."""

    status_code = 400
    error_code = 'validation_error'


class ResourceNotFoundError(APIException):
    """Resource not found in storage."""

    status_code = 404
    error_code = 'resource_not_found'

    def __init__(self, resource_type, resource_id):
        """Initialize resource not found error.

        Args:
            resource_type: Type of resource (e.g., 'World', 'Story', 'User').
                Looked up via t('resources.<lowercase>'); falls back to the
                raw value if no translation key exists.
            resource_id: ID of the missing resource
        """
        # Lazy import to avoid a circular dependency between core.exceptions
        # and utils (utils.validation imports from core.exceptions).
        from utils.i18n import t
        type_key = f'resources.{resource_type.lower()}'
        type_label = t(type_key)
        if type_label == type_key:
            type_label = resource_type
        message = t('errors.resource_not_found', type=type_label, id=resource_id)
        details = {
            'resource_type': resource_type,
            'resource_id': resource_id
        }
        super().__init__(message, details)


class PermissionDeniedError(APIException):
    """User lacks permission for this action."""

    status_code = 403
    error_code = 'permission_denied'

    def __init__(self, action, resource_type=None):
        """Initialize permission denied error.

        Args:
            action: Action being attempted (e.g., 'view', 'edit', 'delete').
                Looked up via t('actions.<value>'); falls back to the raw
                value if no translation key exists.
            resource_type: Type of resource (optional). Looked up via
                t('resources.<lowercase>') with the same fallback rule.
        """
        # Lazy import to avoid a circular dependency.
        from utils.i18n import t
        action_key = f'actions.{action}'
        action_label = t(action_key)
        if action_label == action_key:
            action_label = action

        if resource_type:
            type_key = f'resources.{resource_type.lower()}'
            type_label = t(type_key)
            if type_label == type_key:
                type_label = resource_type
            message = t('errors.permission_denied', action=action_label, type=type_label)
        else:
            message = f"Permission denied: {action_label}"

        details = {
            'action': action,
            'resource_type': resource_type
        }
        super().__init__(message, details)


class BusinessRuleError(APIException):
    """Business rule or constraint violation."""

    status_code = 400
    error_code = 'business_rule_violation'


class AuthenticationError(APIException):
    """Authentication failed or token invalid."""

    status_code = 401
    error_code = 'authentication_error'


class QuotaExceededError(APIException):
    """User quota or rate limit exceeded."""

    status_code = 429
    error_code = 'quota_exceeded'

    def __init__(self, message, current_count=None, limit=None):
        """Initialize quota exceeded error.

        Args:
            message: Human-readable error message
            current_count: Current usage count
            limit: Maximum allowed count
        """
        details = {}
        if current_count is not None:
            details['current_count'] = current_count
        if limit is not None:
            details['limit'] = limit

        super().__init__(message, details)


class ConflictError(APIException):
    """Resource conflict (e.g., duplicate username/email)."""

    status_code = 409
    error_code = 'conflict'


class ExternalServiceError(APIException):
    """External service (GPT, Facebook API, etc.) error."""

    status_code = 502
    error_code = 'external_service_error'

    def __init__(self, service_name, message, original_error=None):
        """Initialize external service error.

        Args:
            service_name: Name of the external service
            message: Human-readable error message
            original_error: Original exception (optional)
        """
        details = {
            'service': service_name
        }
        if original_error:
            details['original_error'] = str(original_error)

        super().__init__(message, details)
