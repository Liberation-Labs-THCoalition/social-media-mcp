"""Platform clients for social media posting."""

from platforms.base import BasePlatform
from platforms.bluesky import BlueSkyPlatform
from platforms.mastodon import MastodonPlatform
from platforms.facebook import FacebookPlatform
from platforms.instagram import InstagramPlatform
from platforms.linkedin import LinkedInPlatform
from platforms.twitter import TwitterPlatform


def get_platform(name: str) -> BasePlatform:
    """Get platform client by name."""
    platforms = {
        "bluesky": BlueSkyPlatform,
        "mastodon": MastodonPlatform,
        "facebook": FacebookPlatform,
        "instagram": InstagramPlatform,
        "linkedin": LinkedInPlatform,
        "twitter": TwitterPlatform,
    }
    cls = platforms.get(name.lower())
    if not cls:
        raise ValueError(f"Unknown platform: {name}. Available: {list(platforms.keys())}")
    return cls()
