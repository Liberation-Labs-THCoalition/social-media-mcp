"""Configuration management for social media MCP server."""

import json
import os
from pathlib import Path


# Platform credentials from environment
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE", "")
BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD", "")

MASTODON_INSTANCE = os.getenv("MASTODON_INSTANCE", "https://mastodon.social")
MASTODON_ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN", "")

FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")

INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_ORG_ID = os.getenv("LINKEDIN_ORG_ID", "")

# OpenAI for content generation
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Google Sheets
CONTENT_QUEUE_SHEET_ID = os.getenv(
    "CONTENT_QUEUE_SHEET_ID",
    "1zbb1Iu1g6OlSmf7NWq8hl6YKXUODh4EoxknLHJEehWA"
)
QUEUE_TAB = os.getenv("QUEUE_TAB", "Queue")
ANALYTICS_TAB = os.getenv("ANALYTICS_TAB", "Analytics")

# Brand voice config file
BRAND_VOICE_PATH = os.getenv(
    "BRAND_VOICE_PATH",
    str(Path(__file__).parent.parent / "brand_voice.json")
)


def get_brand_voice() -> dict:
    """Load brand voice from JSON file."""
    try:
        with open(BRAND_VOICE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "org_name": "Coalition",
            "tone": "Professional but approachable",
            "values": ["transparency", "community", "ethics"],
            "avoid": ["corporate jargon", "fear-based messaging"],
            "audience": "Community members, advocates, and allies",
            "hashtags": {}
        }


def save_brand_voice(voice: dict):
    """Save brand voice to JSON file."""
    with open(BRAND_VOICE_PATH, "w") as f:
        json.dump(voice, f, indent=2)


def is_platform_configured(platform: str) -> bool:
    """Check if a platform has credentials configured."""
    checks = {
        "bluesky": bool(BLUESKY_HANDLE and BLUESKY_APP_PASSWORD),
        "mastodon": bool(MASTODON_ACCESS_TOKEN),
        "facebook": bool(FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID),
        "instagram": bool(INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID),
        "linkedin": bool(LINKEDIN_ACCESS_TOKEN),
        "twitter": False,  # Stub only
    }
    return checks.get(platform, False)
