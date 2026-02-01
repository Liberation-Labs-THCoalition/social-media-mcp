"""Instagram platform client (stub)."""

from typing import Optional
from platforms.base import BasePlatform


class InstagramPlatform(BasePlatform):
    name = "instagram"
    max_length = 2200
    is_stub = True

    async def post(self, text: str, media_urls: Optional[list[str]] = None) -> dict:
        raise NotImplementedError("Instagram integration not yet configured. Requires Meta Graph API OAuth app approval.")

    async def get_metrics(self, post_id: str) -> dict:
        return {"likes": 0, "reposts": 0, "replies": 0, "impressions": 0}

    async def verify_credentials(self) -> bool:
        return False
