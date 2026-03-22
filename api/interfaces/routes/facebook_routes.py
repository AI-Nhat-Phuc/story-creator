"""Facebook API routes for the Story Creator backend."""

from flask import Blueprint, request, jsonify, g
from core.exceptions import (
    PermissionDeniedError,
    ValidationError as APIValidationError,
    ExternalServiceError,
    BusinessRuleError
)
from utils.responses import success_response
from interfaces.auth_middleware import token_required
import uuid
import threading
import logging

logger = logging.getLogger(__name__)


def _require_facebook_access(current_user):
    """Raise PermissionDeniedError if user lacks facebook_access."""
    if not current_user.metadata.get('facebook_access', False):
        raise PermissionDeniedError(
            'access Facebook management features',
            'this account'
        )


def _check_fb_result(result):
    """Raise ExternalServiceError if Facebook API returned an error."""
    if 'error' in result:
        err = result['error']
        message = err.get('message', str(err)) if isinstance(err, dict) else str(err)
        raise ExternalServiceError('Facebook Graph API', message)


def create_facebook_bp(facebook_service, gpt_results, has_gpt):
    """Create and configure the Facebook blueprint.

    Args:
        facebook_service: FacebookService instance
        gpt_results: Shared TaskStore for async GPT results
        has_gpt: Boolean indicating if GPT is available

    Returns:
        Blueprint: Configured Flask blueprint for Facebook routes
    """
    fb_bp = Blueprint('facebook', __name__)

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    @fb_bp.route('/api/facebook/token/exchange', methods=['POST'])
    @token_required
    def exchange_token():
        """Exchange a short-lived Facebook token for a long-lived one.
        ---
        tags:
          - Facebook
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                short_token:
                  type: string
                  description: Short-lived access token from Facebook Login
        responses:
          200:
            description: Long-lived token returned
          400:
            description: Missing token
          403:
            description: Facebook access not granted
        """
        _require_facebook_access(g.current_user)

        data = request.json or {}
        short_token = data.get('short_token', '').strip()
        if not short_token:
            raise APIValidationError('short_token is required')

        result = facebook_service.exchange_short_token(short_token)
        _check_fb_result(result)
        return success_response(result)

    @fb_bp.route('/api/facebook/pages', methods=['GET'])
    @token_required
    def list_pages():
        """Get pages managed by the authenticated Facebook user.
        ---
        tags:
          - Facebook
        parameters:
          - name: fb_token
            in: query
            type: string
            required: true
            description: Facebook user access token
        responses:
          200:
            description: List of pages
          400:
            description: Missing token
          403:
            description: Facebook access not granted
        """
        _require_facebook_access(g.current_user)

        fb_token = request.args.get('fb_token', '').strip()
        if not fb_token:
            raise APIValidationError('fb_token query parameter is required')

        result = facebook_service.get_page_tokens(fb_token)
        _check_fb_result(result)
        return success_response(result)

    # ------------------------------------------------------------------
    # User info
    # ------------------------------------------------------------------

    @fb_bp.route('/api/facebook/me', methods=['GET'])
    @token_required
    def get_me():
        """Get info about the Facebook token owner.
        ---
        tags:
          - Facebook
        parameters:
          - name: fb_token
            in: query
            type: string
            required: true
        responses:
          200:
            description: User info
          403:
            description: Facebook access not granted
        """
        _require_facebook_access(g.current_user)

        fb_token = request.args.get('fb_token', '').strip()
        if not fb_token:
            raise APIValidationError('fb_token is required')

        result = facebook_service.get_user_info(fb_token)
        _check_fb_result(result)
        return success_response(result)

    # ------------------------------------------------------------------
    # Posts
    # ------------------------------------------------------------------

    @fb_bp.route('/api/facebook/pages/<page_id>/posts', methods=['GET'])
    @token_required
    def get_posts(page_id):
        """Get posts from a Facebook page.
        ---
        tags:
          - Facebook
        parameters:
          - name: page_id
            in: path
            type: string
            required: true
          - name: fb_token
            in: query
            type: string
            required: true
          - name: limit
            in: query
            type: integer
            default: 10
        responses:
          200:
            description: List of posts
          403:
            description: Facebook access not granted
        """
        _require_facebook_access(g.current_user)

        fb_token = request.args.get('fb_token', '').strip()
        if not fb_token:
            raise APIValidationError('fb_token is required')

        limit = request.args.get('limit', 10, type=int)
        result = facebook_service.get_page_posts(page_id, fb_token, limit=limit)
        _check_fb_result(result)
        return success_response(result)

    @fb_bp.route('/api/facebook/posts/<post_id>', methods=['GET'])
    @token_required
    def get_post(post_id):
        """Get details of a single Facebook post.
        ---
        tags:
          - Facebook
        parameters:
          - name: post_id
            in: path
            type: string
            required: true
          - name: fb_token
            in: query
            type: string
            required: true
        responses:
          200:
            description: Post details with engagement
          403:
            description: Facebook access not granted
        """
        _require_facebook_access(g.current_user)

        fb_token = request.args.get('fb_token', '').strip()
        if not fb_token:
            raise APIValidationError('fb_token is required')

        result = facebook_service.get_post_detail(post_id, fb_token)
        _check_fb_result(result)
        return success_response(result)

    @fb_bp.route('/api/facebook/posts/<post_id>/comments', methods=['GET'])
    @token_required
    def get_comments(post_id):
        """Get comments on a Facebook post.
        ---
        tags:
          - Facebook
        parameters:
          - name: post_id
            in: path
            type: string
            required: true
          - name: fb_token
            in: query
            type: string
            required: true
          - name: limit
            in: query
            type: integer
            default: 25
        responses:
          200:
            description: List of comments
          403:
            description: Facebook access not granted
        """
        _require_facebook_access(g.current_user)

        fb_token = request.args.get('fb_token', '').strip()
        if not fb_token:
            raise APIValidationError('fb_token is required')

        limit = request.args.get('limit', 25, type=int)
        result = facebook_service.get_post_comments(post_id, fb_token, limit=limit)
        _check_fb_result(result)
        return success_response(result)

    # ------------------------------------------------------------------
    # Publish
    # ------------------------------------------------------------------

    @fb_bp.route('/api/facebook/pages/<page_id>/posts', methods=['POST'])
    @token_required
    def create_post(page_id):
        """Create a new post on a Facebook page.
        ---
        tags:
          - Facebook
        parameters:
          - name: page_id
            in: path
            type: string
            required: true
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                fb_token:
                  type: string
                  description: Page access token with publish permissions
                message:
                  type: string
                link:
                  type: string
                image_url:
                  type: string
        responses:
          200:
            description: Created post id
          400:
            description: Validation error
          403:
            description: Facebook access not granted
        """
        _require_facebook_access(g.current_user)

        data = request.json or {}
        fb_token = data.get('fb_token', '').strip()
        if not fb_token:
            raise APIValidationError('fb_token is required')

        message = data.get('message', '').strip()
        link = data.get('link', '').strip()
        image_url = data.get('image_url', '').strip()

        if not message and not link and not image_url:
            raise APIValidationError('At least message, link, or image_url is required')

        result = facebook_service.create_post(
            page_id, fb_token,
            message=message, link=link, image_url=image_url
        )
        _check_fb_result(result)
        return success_response(result)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    @fb_bp.route('/api/facebook/pages/<page_id>/search', methods=['GET'])
    @token_required
    def search_posts(page_id):
        """Search posts on a page by keyword.
        ---
        tags:
          - Facebook
        parameters:
          - name: page_id
            in: path
            type: string
            required: true
          - name: fb_token
            in: query
            type: string
            required: true
          - name: keyword
            in: query
            type: string
            required: true
          - name: limit
            in: query
            type: integer
            default: 25
        responses:
          200:
            description: Matching posts
          400:
            description: Missing parameters
          403:
            description: Facebook access not granted
        """
        _require_facebook_access(g.current_user)

        fb_token = request.args.get('fb_token', '').strip()
        keyword = request.args.get('keyword', '').strip()

        if not fb_token:
            raise APIValidationError('fb_token is required')
        if not keyword:
            raise APIValidationError('keyword is required')

        limit = request.args.get('limit', 25, type=int)
        result = facebook_service.search_page_posts(page_id, fb_token, keyword, limit=limit)
        _check_fb_result(result)
        return success_response(result)

    # ------------------------------------------------------------------
    # GPT content generation
    # ------------------------------------------------------------------

    @fb_bp.route('/api/facebook/generate-content', methods=['POST'])
    @token_required
    def generate_content():
        """Generate Facebook post content using GPT.
        ---
        tags:
          - Facebook
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - topic
              properties:
                topic:
                  type: string
                  example: "Khuyến mãi mùa hè"
                requirements:
                  type: string
                  example: "Nhấn mạnh giảm giá 50%"
                tone:
                  type: string
                  enum: [professional, casual, creative, humorous]
                  default: professional
        responses:
          200:
            description: Task created (async)
          400:
            description: Missing topic
          403:
            description: Facebook access not granted
          503:
            description: GPT not available
        """
        _require_facebook_access(g.current_user)

        if not has_gpt:
            raise ExternalServiceError('GPT', 'GPT not available')

        data = request.json or {}
        topic = data.get('topic', '').strip()
        if not topic:
            raise APIValidationError('topic is required')

        requirements = data.get('requirements', '')
        tone = data.get('tone', 'professional')

        task_id = str(uuid.uuid4())
        gpt_results.set(task_id, {'status': 'pending'})

        def background_generate():
            try:
                content = facebook_service.generate_post_content(
                    topic, requirements=requirements, tone=tone
                )
                if content:
                    gpt_results.set(task_id, {
                        'status': 'completed',
                        'result': {'content': content}
                    })
                else:
                    gpt_results.set(task_id, {
                        'status': 'error',
                        'result': 'Failed to generate content'
                    })
            except Exception as e:
                logger.error(f"GPT generate content error: {e}")
                gpt_results.set(task_id, {'status': 'error', 'result': str(e)})

        thread = threading.Thread(target=background_generate, daemon=True)
        thread.start()
        return jsonify({'task_id': task_id})

    return fb_bp
