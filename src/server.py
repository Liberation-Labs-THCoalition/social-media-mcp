"""Social Media Management MCP Server - FastMCP entry point."""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server import FastMCP

from models import QueueItem, PostStatus, Platform, LIVE_PLATFORMS, STUB_PLATFORMS, PLATFORM_LIMITS
from platforms import get_platform
import config
import content
import sheets

mcp = FastMCP("social-media")


@mcp.tool()
async def sm_create_content(topic: str, platforms: str = "bluesky,mastodon", tone: str = "", org: str = "") -> str:
    """Generate AI content drafts for the given topic and save to the content queue sheet.

    Args:
        topic: The content topic or idea to generate posts about
        platforms: Comma-separated platform names (bluesky, mastodon, linkedin, facebook, instagram)
        tone: Optional tone override (defaults to brand voice)
        org: Optional organization name override (defaults to brand voice)
    """
    try:
        platform_list = [p.strip() for p in platforms.split(",") if p.strip()]
        drafts = await content.generate_content(
            topic=topic,
            platforms=platform_list,
            tone=tone,
            org=org,
        )
        content_id = f"SM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        item = QueueItem(
            content_id=content_id,
            topic=topic,
            org=org or config.get_brand_voice().get("org_name", ""),
            tone=tone or config.get_brand_voice().get("tone", ""),
            bluesky_draft=drafts.get("bluesky", ""),
            mastodon_draft=drafts.get("mastodon", ""),
            linkedin_draft=drafts.get("linkedin", ""),
            facebook_draft=drafts.get("facebook", ""),
            instagram_draft=drafts.get("instagram", ""),
            status=PostStatus.DRAFT,
            created_at=datetime.now().isoformat(),
        )
        row = sheets.append_queue_item(item)
        return json.dumps({
            "success": True,
            "content_id": content_id,
            "row": row,
            "platforms": platform_list,
            "drafts": drafts,
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_edit_draft(queue_row: int, platform: str, new_text: str) -> str:
    """Update a draft's text for a specific platform in the queue.

    Args:
        queue_row: The sheet row number of the queue item
        platform: Platform name (bluesky, mastodon, etc.)
        new_text: The new draft text
    """
    try:
        col_name = f"{platform}_draft"
        sheets.update_queue_row(queue_row, {col_name: new_text})
        return json.dumps({"success": True, "row": queue_row, "platform": platform})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_list_queue(status: str = "", limit: int = 20) -> str:
    """List content queue items, optionally filtered by status.

    Args:
        status: Filter by status (Draft, Pending Review, Approved, Scheduled, Posted, Failed)
        limit: Maximum items to return
    """
    try:
        items = sheets.get_queue_items(status_filter=status, limit=limit)
        return json.dumps({"success": True, "count": len(items), "items": items})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_approve(queue_row: int) -> str:
    """Mark a queue item as Approved for posting.

    Args:
        queue_row: The sheet row number to approve
    """
    try:
        sheets.update_queue_row(queue_row, {"status": PostStatus.APPROVED.value})
        return json.dumps({"success": True, "row": queue_row, "status": "Approved"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_schedule(queue_row: int, scheduled_for: str) -> str:
    """Schedule an approved queue item for a specific publish time.

    Args:
        queue_row: The sheet row number to schedule
        scheduled_for: ISO datetime string for when to publish
    """
    try:
        sheets.update_queue_row(queue_row, {
            "status": PostStatus.SCHEDULED.value,
            "scheduled_for": scheduled_for,
        })
        return json.dumps({"success": True, "row": queue_row, "status": "Scheduled", "scheduled_for": scheduled_for})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_update_status(queue_row: int, status: str) -> str:
    """Manually update a queue item's status.

    Args:
        queue_row: The sheet row number
        status: New status (Draft, Pending Review, Approved, Scheduled, Posted, Failed)
    """
    try:
        sheets.update_queue_row(queue_row, {"status": status})
        return json.dumps({"success": True, "row": queue_row, "status": status})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_post_now(queue_row: int, platforms: str = "") -> str:
    """Post a queue item immediately to specified (or all drafted) platforms.

    Args:
        queue_row: The sheet row number to post
        platforms: Comma-separated platforms to post to (empty = all with drafts)
    """
    try:
        item = sheets.get_queue_item(queue_row)
        if not item:
            return json.dumps({"success": False, "error": f"No item at row {queue_row}"})

        # Determine which platforms to post to
        draft_fields = {
            "bluesky": item.get("bluesky_draft", ""),
            "mastodon": item.get("mastodon_draft", ""),
            "linkedin": item.get("linkedin_draft", ""),
            "facebook": item.get("facebook_draft", ""),
            "instagram": item.get("instagram_draft", ""),
        }

        if platforms:
            target_platforms = [p.strip() for p in platforms.split(",") if p.strip()]
        else:
            target_platforms = [p for p, text in draft_fields.items() if text.strip()]

        results = {}
        post_ids = {}
        for plat in target_platforms:
            draft_text = draft_fields.get(plat, "")
            if not draft_text.strip():
                results[plat] = {"posted": False, "error": "No draft text"}
                continue
            try:
                client = get_platform(plat)
                result = await client.post(draft_text)
                pid = result.get("post_id", "")
                post_ids[plat] = pid
                results[plat] = {"posted": True, "post_id": pid, "url": result.get("url", "")}
            except Exception as pe:
                results[plat] = {"posted": False, "error": str(pe)}

        any_posted = any(r.get("posted") for r in results.values())
        new_status = PostStatus.POSTED.value if any_posted else PostStatus.FAILED.value
        sheets.update_queue_row(queue_row, {
            "status": new_status,
            "posted_at": datetime.now().isoformat(),
            "post_ids": json.dumps(post_ids),
        })

        return json.dumps({
            "success": True,
            "row": queue_row,
            "status": new_status,
            "results": results,
            "post_ids": post_ids,
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_post_text(text: str, platform: str) -> str:
    """Quick one-off post directly to a platform, bypassing the queue.

    Args:
        text: The text to post
        platform: Target platform (bluesky, mastodon, etc.)
    """
    try:
        client = get_platform(platform)
        result = await client.post(text)
        return json.dumps({"success": True, "platform": platform, "result": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_get_analytics(platform: str = "", days: int = 7) -> str:
    """View posting analytics from the analytics sheet.

    Args:
        platform: Filter by platform (empty = all)
        days: Number of days to look back
    """
    try:
        data = sheets.get_analytics(platform=platform, days=days)
        return json.dumps({"success": True, "days": days, "platform": platform or "all", "count": len(data), "analytics": data})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_refresh_analytics(post_id: str = "") -> str:
    """Fetch fresh engagement metrics from platform APIs.

    Args:
        post_id: Specific post ID to refresh (empty = refresh all recent)
    """
    try:
        if post_id:
            record = sheets.get_analytics_for_post(post_id)
            if not record:
                return json.dumps({"success": False, "error": f"No record for post {post_id}"})
            plat = record.get("platform", "")
            client = get_platform(plat)
            metrics = await client.get_metrics(post_id)
            sheets.update_analytics(post_id, metrics)
            return json.dumps({"success": True, "post_id": post_id, "metrics": metrics})
        else:
            recent = sheets.get_recent_post_ids()
            refreshed = []
            for pid, plat in recent:
                try:
                    client = get_platform(plat)
                    metrics = await client.get_metrics(pid)
                    sheets.update_analytics(pid, metrics)
                    refreshed.append({"post_id": pid, "platform": plat, "metrics": metrics})
                except Exception as pe:
                    refreshed.append({"post_id": pid, "platform": plat, "error": str(pe)})
            return json.dumps({"success": True, "refreshed": refreshed})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_list_accounts() -> str:
    """Show configured platform accounts and whether they are live or stub."""
    try:
        accounts = []
        all_platforms = sorted(set(p.value for p in LIVE_PLATFORMS) | set(p.value for p in STUB_PLATFORMS))
        for plat in all_platforms:
            accounts.append({
                "platform": plat,
                "configured": config.is_platform_configured(plat),
                "mode": "live" if Platform(plat) in LIVE_PLATFORMS else "stub",
            })
        return json.dumps({"success": True, "accounts": accounts})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_test_account(platform: str) -> str:
    """Verify that credentials work for a platform.

    Args:
        platform: Platform name to test (bluesky, mastodon, etc.)
    """
    try:
        client = get_platform(platform)
        result = await client.verify_credentials()
        return json.dumps({"success": True, "platform": platform, "verified": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_get_brand_voice() -> str:
    """Return the current brand voice configuration."""
    try:
        voice = config.get_brand_voice()
        return json.dumps({"success": True, "brand_voice": voice})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_set_brand_voice(voice_json: str) -> str:
    """Update the brand voice configuration.

    Args:
        voice_json: JSON string with brand voice settings (org_name, tone, values, avoid, audience, hashtags)
    """
    try:
        voice = json.loads(voice_json)
        config.save_brand_voice(voice)
        return json.dumps({"success": True, "brand_voice": voice})
    except json.JSONDecodeError as e:
        return json.dumps({"success": False, "error": f"Invalid JSON: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def sm_get_platform_status() -> str:
    """Show which platforms are live (fully implemented) vs stub (placeholder)."""
    try:
        return json.dumps({
            "success": True,
            "live": [p.value for p in LIVE_PLATFORMS],
            "stub": [p.value for p in STUB_PLATFORMS],
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


if __name__ == "__main__":
    mcp.run()
