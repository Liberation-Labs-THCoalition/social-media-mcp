"""X/Twitter platform client (stub only - excluded for ethics)."""

from typing import Optional
from platforms.base import BasePlatform


class TwitterPlatform(BasePlatform):
    name = "twitter"
    max_length = 280
    is_stub = True

    async def post(self, text: str, media_urls: Optional[list[str]] = None) -> dict:
        raise NotImplementedError("X/Twitter integration is excluded. Stub only.")

    async def get_metrics(self, post_id: str) -> dict:
        return {"likes": 0, "reposts": 0, "replies": 0, "impressions": 0}

    async def verify_credentials(self) -> bool:
        return False
