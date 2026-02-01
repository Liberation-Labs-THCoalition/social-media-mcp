"""Data models for social media MCP server."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class PostStatus(str, Enum):
    DRAFT = "Draft"
    PENDING_REVIEW = "Pending Review"
    APPROVED = "Approved"
    SCHEDULED = "Scheduled"
    POSTED = "Posted"
    FAILED = "Failed"


class Platform(str, Enum):
    BLUESKY = "bluesky"
    MASTODON = "mastodon"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"


# Character limits per platform
PLATFORM_LIMITS = {
    Platform.BLUESKY: 300,
    Platform.MASTODON: 500,
    Platform.FACEBOOK: 63206,
    Platform.INSTAGRAM: 2200,
    Platform.LINKEDIN: 3000,
    Platform.TWITTER: 280,
}

# Platforms that are fully implemented (not stubs)
LIVE_PLATFORMS = {Platform.BLUESKY, Platform.MASTODON}

# Stub-only platforms
STUB_PLATFORMS = {Platform.FACEBOOK, Platform.INSTAGRAM, Platform.LINKEDIN, Platform.TWITTER}


@dataclass
class QueueItem:
    content_id: str
    topic: str
    org: str
    tone: str
    bluesky_draft: str = ""
    mastodon_draft: str = ""
    linkedin_draft: str = ""
    facebook_draft: str = ""
    instagram_draft: str = ""
    status: PostStatus = PostStatus.DRAFT
    created_at: str = ""
    scheduled_for: str = ""
    posted_at: str = ""
    post_ids: str = ""

    def get_draft(self, platform: Platform) -> str:
        return getattr(self, f"{platform.value}_draft", "")

    def set_draft(self, platform: Platform, text: str):
        setattr(self, f"{platform.value}_draft", text)

    def to_row(self) -> list[str]:
        return [
            self.content_id, self.topic, self.org, self.tone,
            self.bluesky_draft, self.mastodon_draft, self.linkedin_draft,
            self.facebook_draft, self.instagram_draft,
            self.status.value, self.created_at, self.scheduled_for,
            self.posted_at, self.post_ids,
        ]

    @classmethod
    def from_row(cls, row: list[str]) -> "QueueItem":
        # Pad row to expected length
        while len(row) < 14:
            row.append("")
        return cls(
            content_id=row[0], topic=row[1], org=row[2], tone=row[3],
            bluesky_draft=row[4], mastodon_draft=row[5], linkedin_draft=row[6],
            facebook_draft=row[7], instagram_draft=row[8],
            status=PostStatus(row[9]) if row[9] else PostStatus.DRAFT,
            created_at=row[10], scheduled_for=row[11],
            posted_at=row[12], post_ids=row[13],
        )

    @classmethod
    def header_row(cls) -> list[str]:
        return [
            "content_id", "topic", "org", "tone",
            "bluesky_draft", "mastodon_draft", "linkedin_draft",
            "facebook_draft", "instagram_draft",
            "status", "created_at", "scheduled_for", "posted_at", "post_ids",
        ]


@dataclass
class AnalyticsRecord:
    post_id: str
    platform: str
    content_id: str
    posted_at: str
    likes: int = 0
    reposts: int = 0
    replies: int = 0
    impressions: int = 0
    collected_at: str = ""

    def to_row(self) -> list[str]:
        return [
            self.post_id, self.platform, self.content_id, self.posted_at,
            str(self.likes), str(self.reposts), str(self.replies),
            str(self.impressions), self.collected_at,
        ]

    @classmethod
    def header_row(cls) -> list[str]:
        return [
            "post_id", "platform", "content_id", "posted_at",
            "likes", "reposts", "replies", "impressions", "collected_at",
        ]


@dataclass
class PostResult:
    success: bool
    platform: str
    post_id: str = ""
    url: str = ""
    error: str = ""


@dataclass
class BrandVoice:
    org_name: str = "Coalition"
    tone: str = "Professional but approachable"
    values: list[str] = field(default_factory=lambda: ["transparency", "community", "ethics"])
    avoid: list[str] = field(default_factory=lambda: ["corporate jargon", "fear-based messaging"])
    audience: str = "Community members, advocates, and allies"
    hashtags: dict[str, list[str]] = field(default_factory=dict)
