"""Request validation utilities using Marshmallow schemas."""

from functools import wraps
from flask import request, g
from marshmallow import ValidationError as MarshmallowValidationError
from core.exceptions import ValidationError, ResourceNotFoundError, PermissionDeniedError
from utils.responses import paginated_response


def validate_request(schema_class, location='json'):
    """Decorator to validate request data against Marshmallow schema.

    Args:
        schema_class: Marshmallow schema class to validate against
        location: Where to get data from ('json', 'args', 'form')

    Returns:
        Decorator that validates request and stores result in request.validated_data

    Raises:
        ValidationError: If validation fails

    Example:
        >>> @world_bp.route('/api/worlds', methods=['POST'])
        >>> @token_required
        >>> @validate_request(CreateWorldSchema)
        >>> def create_world():
        >>>     data = request.validated_data  # Already validated
        >>>     ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            schema = schema_class()

            # Get data from appropriate location
            if location == 'json':
                data = request.json or {}
            elif location == 'args':
                data = request.args.to_dict()
            elif location == 'form':
                data = request.form.to_dict()
            else:
                raise ValueError(f"Invalid location: {location}")

            # Validate
            try:
                validated_data = schema.load(data)
                request.validated_data = validated_data
                return f(*args, **kwargs)
            except MarshmallowValidationError as e:
                raise ValidationError(
                    'Request validation failed',
                    details=e.messages
                )

        return decorated
    return decorator


def validate_query_params(schema_class):
    """Decorator to validate query parameters.

    Args:
        schema_class: Marshmallow schema class

    Returns:
        Decorator that validates query params

    Example:
        >>> @world_bp.route('/api/worlds', methods=['GET'])
        >>> @validate_query_params(ListWorldsQuerySchema)
        >>> def list_worlds():
        >>>     params = request.validated_data
        >>>     page = params.get('page', 1)
        >>>     ...
    """
    return validate_request(schema_class, location='args')


def extract_pagination(items_loader):
    """Decorator that loads all items, slices them by page/per_page, and returns paginated_response.

    Must be used after @validate_query_params so that request.validated_data has 'page'/'per_page'.

    Args:
        items_loader: Callable called with no args (inside the request context) that returns the
                      full list of items to paginate.

    Example:
        >>> @world_bp.route('/api/worlds', methods=['GET'])
        >>> @optional_auth
        >>> @validate_query_params(ListWorldsQuerySchema)
        >>> @extract_pagination(lambda: storage.list_worlds())
        >>> def list_worlds():
        >>>     pass  # Response is built automatically by the decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            params = getattr(request, 'validated_data', {})
            page = params.get('page', 1)
            per_page = params.get('per_page', 20)

            all_items = items_loader()
            total = len(all_items)
            start = (page - 1) * per_page
            items = all_items[start:start + per_page]

            return paginated_response(items, page, per_page, total)
        return decorated
    return decorator


def require_ownership(loader, resource_name='Resource', id_param='id', allow_shared=False):
    """Decorator that loads a resource and enforces that the current user owns it.

    Must be used after @token_required so that g.current_user is set.

    Args:
        loader: Callable(resource_id) → resource dict or None
        resource_name: Human-readable name for error messages (e.g. 'World', 'Story')
        id_param: URL path parameter name for the resource id (default 'id')
        allow_shared: If True, also allow users listed in resource['shared_with']

    Stores the loaded resource in request.resource for use inside the route.

    Example:
        >>> @world_bp.route('/api/worlds/<world_id>', methods=['DELETE'])
        >>> @token_required
        >>> @require_ownership(lambda wid: storage.load_world(wid), 'World', 'world_id')
        >>> def delete_world(world_id):
        >>>     world = request.resource  # Already loaded & ownership verified
        >>>     storage.delete_world(world_id)
        >>>     return deleted_response('World deleted')
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            resource_id = kwargs.get(id_param)
            resource = loader(resource_id)

            if not resource:
                raise ResourceNotFoundError(resource_name, resource_id)

            current_user = g.current_user
            owner_id = resource.get('owner_id')
            is_admin = getattr(current_user, 'role', '') in ('admin', 'moderator')
            is_owner = owner_id == current_user.user_id
            is_shared = allow_shared and current_user.user_id in resource.get('shared_with', [])

            if not (is_owner or is_admin or is_shared):
                raise PermissionDeniedError(f'modify this {resource_name.lower()}')

            request.resource = resource
            return f(*args, **kwargs)
        return decorated
    return decorator
