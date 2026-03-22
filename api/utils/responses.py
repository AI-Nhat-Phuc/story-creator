"""Standardized response utilities for consistent API responses."""

from flask import jsonify


def success_response(data, message=None, status=200):
    """Return standardized success response.

    Args:
        data: Response data (dict, list, or None)
        message: Optional success message
        status: HTTP status code (default: 200)

    Returns:
        Flask JSON response with standardized format

    Example:
        >>> success_response({'world_id': '123'}, 'World created')
        {'success': True, 'data': {'world_id': '123'}, 'message': 'World created'}, 200
    """
    response = {
        'success': True,
        'data': data
    }

    if message:
        response['message'] = message

    return jsonify(response), status


def paginated_response(items, page, per_page, total):
    """Return paginated list response with metadata.

    Args:
        items: List of items for current page
        page: Current page number (1-indexed)
        per_page: Items per page
        total: Total number of items across all pages

    Returns:
        Flask JSON response with pagination metadata

    Example:
        >>> paginated_response([{...}, {...}], page=2, per_page=10, total=25)
        {
            'success': True,
            'data': [{...}, {...}],
            'pagination': {
                'page': 2,
                'per_page': 10,
                'total': 25,
                'total_pages': 3
            }
        }, 200
    """
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

    response = {
        'success': True,
        'data': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages
        }
    }

    return jsonify(response), 200


def created_response(data, message="Resource created successfully"):
    """Return 201 Created response.

    Args:
        data: Created resource data
        message: Success message (default: "Resource created successfully")

    Returns:
        Flask JSON response with 201 status code

    Example:
        >>> created_response({'world_id': '123'})
        {'success': True, 'data': {'world_id': '123'}, 'message': '...'}, 201
    """
    return success_response(data, message, status=201)


def deleted_response(message="Resource deleted successfully"):
    """Return success response for deletion.

    Args:
        message: Success message (default: "Resource deleted successfully")

    Returns:
        Flask JSON response with 200 status code and null data

    Example:
        >>> deleted_response("World deleted")
        {'success': True, 'data': None, 'message': 'World deleted'}, 200
    """
    return success_response(None, message, status=200)


def accepted_response(data=None, message="Request accepted for processing"):
    """Return 202 Accepted response for async operations.

    Args:
        data: Optional data (e.g., task ID)
        message: Message indicating async processing

    Returns:
        Flask JSON response with 202 status code

    Example:
        >>> accepted_response({'task_id': 'abc123'}, 'GPT generation started')
        {'success': True, 'data': {'task_id': 'abc123'}, 'message': '...'}, 202
    """
    return success_response(data, message, status=202)


def no_content_response():
    """Return 204 No Content response.

    Returns:
        Empty response with 204 status code

    Example:
        >>> no_content_response()
        '', 204
    """
    return '', 204
