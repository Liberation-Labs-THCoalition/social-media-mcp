"""LinkedIn platform client (stub)."""

from typing import Optional
from platforms.base import BasePlatform


class LinkedInPlatform(BasePlatform):
    name = "linkedin"
    max_length = 3000
    is_stub = True

    async def post(self, text: str, media_urls: Optional[list[str]] = None) -> dict:
        raise NotImplementedError("LinkedIn integration not yet configured. Requires LinkedIn OAuth 2.0 app approval.")

    async def get_metrics(self, post_id: str) -> dict:
        return {"likes": 0, "reposts": 0, "replies": 0, "impressions": 0}

    async def verify_credentials(self) -> bool:
        return False
