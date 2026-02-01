"""Abstract base class for platform clients."""

from abc import ABC, abstractmethod
from typing import Optional


class BasePlatform(ABC):
    """Base class all platform clients inherit from."""

    name: str = "base"
    max_length: int = 500
    is_stub: bool = False

    @abstractmethod
    async def post(self, text: str, media_urls: Optional[list[str]] = None) -> dict:
        """Post content to the platform.

        Returns: {"post_id": str, "url": str}
        Raises: Exception on failure
        """
        ...

    @abstractmethod
    async def get_metrics(self, post_id: str) -> dict:
        """Fetch engagement metrics for a post.

        Returns: {"likes": int, "reposts": int, "replies": int, "impressions": int}
        """
        ...

    @abstractmethod
    async def verify_credentials(self) -> bool:
        """Test that credentials are valid and can connect."""
        ...

    def truncate(self, text: str) -> str:
        """Truncate text to platform's max length."""
        if len(text) <= self.max_length:
            return text
        return text[: self.max_length - 3] + "..."
