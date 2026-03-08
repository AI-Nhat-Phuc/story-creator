"""Facebook Graph API service for managing Facebook Page content."""

import os
import logging
import requests
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


class FacebookService:
    """Service for interacting with Facebook Graph API."""

    def __init__(self, gpt_integration=None):
        """
        Initialize Facebook service.

        Args:
            gpt_integration: Optional GPTIntegration instance for content generation
        """
        self.app_id = os.environ.get("FACEBOOK_APP_ID", "")
        self.app_secret = os.environ.get("FACEBOOK_APP_SECRET", "")
        self.gpt = gpt_integration

    # ------------------------------------------------------------------
    # Token helpers
    # ------------------------------------------------------------------

    def exchange_short_token(self, short_token: str) -> Dict[str, Any]:
        """Exchange a short-lived user token for a long-lived one.

        Args:
            short_token: Short-lived access token from Facebook Login

        Returns:
            dict with access_token, token_type, expires_in
        """
        if not self.app_id or not self.app_secret:
            return {"error": "Facebook App ID and App Secret are required"}

        url = f"{GRAPH_API_BASE}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": short_token,
        }
        resp = requests.get(url, params=params, timeout=15)
        return resp.json()

    def get_page_tokens(self, user_token: str) -> Dict[str, Any]:
        """Get all pages the user manages with their access tokens.

        Args:
            user_token: User access token

        Returns:
            dict with list of pages (id, name, access_token)
        """
        url = f"{GRAPH_API_BASE}/me/accounts"
        params = {"access_token": user_token}
        resp = requests.get(url, params=params, timeout=15)
        return resp.json()

    # ------------------------------------------------------------------
    # User / Page info
    # ------------------------------------------------------------------

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get basic info about the token owner.

        Args:
            access_token: User or page access token

        Returns:
            dict with id, name, etc.
        """
        url = f"{GRAPH_API_BASE}/me"
        params = {
            "fields": "id,name,email,picture",
            "access_token": access_token,
        }
        resp = requests.get(url, params=params, timeout=15)
        return resp.json()

    # ------------------------------------------------------------------
    # Read posts
    # ------------------------------------------------------------------

    def get_page_posts(
        self, page_id: str, access_token: str, limit: int = 10
    ) -> Dict[str, Any]:
        """Get posts from a page.

        Args:
            page_id: Facebook Page ID
            access_token: Page or user access token
            limit: Number of posts to fetch

        Returns:
            dict with data list of posts
        """
        url = f"{GRAPH_API_BASE}/{page_id}/posts"
        params = {
            "fields": "id,message,created_time,full_picture,permalink_url,"
                      "shares,likes.summary(true),comments.summary(true)",
            "limit": min(limit, 100),
            "access_token": access_token,
        }
        resp = requests.get(url, params=params, timeout=15)
        return resp.json()

    def get_post_detail(
        self, post_id: str, access_token: str
    ) -> Dict[str, Any]:
        """Get detailed information about a single post.

        Args:
            post_id: Facebook Post ID
            access_token: Page or user access token

        Returns:
            dict with post details including engagement metrics
        """
        url = f"{GRAPH_API_BASE}/{post_id}"
        params = {
            "fields": "id,message,created_time,full_picture,permalink_url,"
                      "shares,likes.summary(true),comments.summary(true),"
                      "reactions.summary(true)",
            "access_token": access_token,
        }
        resp = requests.get(url, params=params, timeout=15)
        return resp.json()

    def get_post_comments(
        self, post_id: str, access_token: str, limit: int = 25
    ) -> Dict[str, Any]:
        """Get comments on a post.

        Args:
            post_id: Facebook Post ID
            access_token: Page or user access token
            limit: Number of comments to fetch

        Returns:
            dict with data list of comments
        """
        url = f"{GRAPH_API_BASE}/{post_id}/comments"
        params = {
            "fields": "id,message,from,created_time,like_count",
            "limit": min(limit, 100),
            "access_token": access_token,
        }
        resp = requests.get(url, params=params, timeout=15)
        return resp.json()

    # ------------------------------------------------------------------
    # Publish posts
    # ------------------------------------------------------------------

    def create_post(
        self,
        page_id: str,
        access_token: str,
        message: str = "",
        link: str = "",
        image_url: str = "",
    ) -> Dict[str, Any]:
        """Create a new post on a page.

        Args:
            page_id: Facebook Page ID
            access_token: Page access token (must have publish permissions)
            message: Post text content
            link: URL to share
            image_url: URL of image to attach

        Returns:
            dict with id of created post
        """
        if image_url:
            url = f"{GRAPH_API_BASE}/{page_id}/photos"
            data = {
                "url": image_url,
                "caption": message,
                "access_token": access_token,
            }
        else:
            url = f"{GRAPH_API_BASE}/{page_id}/feed"
            data: Dict[str, str] = {
                "message": message,
                "access_token": access_token,
            }
            if link:
                data["link"] = link

        resp = requests.post(url, data=data, timeout=30)
        return resp.json()

    # ------------------------------------------------------------------
    # Search (Page public posts)
    # ------------------------------------------------------------------

    def search_page_posts(
        self, page_id: str, access_token: str, keyword: str, limit: int = 25
    ) -> Dict[str, Any]:
        """Search posts on a page by keyword (client-side filter).

        The Graph API does not offer full-text search on page posts.
        We fetch recent posts and filter locally.

        Args:
            page_id: Facebook Page ID
            access_token: Page or user access token
            keyword: Keyword to search for
            limit: Max posts to scan

        Returns:
            dict with matching posts
        """
        all_posts = self.get_page_posts(page_id, access_token, limit=100)
        if "error" in all_posts:
            return all_posts

        keyword_lower = keyword.lower()
        matched = [
            p
            for p in all_posts.get("data", [])
            if keyword_lower in (p.get("message") or "").lower()
        ]
        return {"data": matched[:limit], "keyword": keyword}

    # ------------------------------------------------------------------
    # GPT content generation
    # ------------------------------------------------------------------

    def generate_post_content(
        self, topic: str, requirements: str = "", tone: str = "professional"
    ) -> Optional[str]:
        """Generate post content using GPT.

        Args:
            topic: Main topic for the post
            requirements: Additional requirements / instructions
            tone: Writing tone (professional, casual, creative, etc.)

        Returns:
            Generated post content string, or None if GPT unavailable
        """
        if not self.gpt:
            return None

        prompt = (
            f"Viết một bài đăng Facebook về chủ đề: {topic}\n"
            f"Giọng văn: {tone}\n"
        )
        if requirements:
            prompt += f"Yêu cầu thêm: {requirements}\n"
        prompt += (
            "\nBài đăng cần hấp dẫn, có emoji phù hợp, "
            "và có lời kêu gọi hành động (CTA). "
            "Chỉ trả về nội dung bài đăng, không giải thích thêm."
        )

        try:
            response = self.gpt.client.chat.completions.create(
                model=self.gpt.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Bạn là chuyên gia viết nội dung mạng xã hội. "
                            "Viết bài đăng Facebook chuyên nghiệp, hấp dẫn, "
                            "tối ưu tương tác."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=500,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"GPT content generation failed: {e}")
            return None
