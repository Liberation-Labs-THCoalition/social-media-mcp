# Social Media Management MCP Server

AI-powered social media management for nonprofits. Full pipeline: content ideation, AI drafting, approval queue, scheduling, cross-platform posting, and analytics.

Built for Coalition and Liberation Labs. Usable by any Claude Code user.

## Quick Start

### 1. Install Dependencies

```bash
cd social-media-mcp
pip install -r requirements.txt
```

### 2. Configure Credentials

Copy `.env.example` to `.env` and fill in your platform credentials:

```bash
cp .env.example .env
# Edit .env with your credentials
```

At minimum you need:
- **OpenAI API key** (for content generation)
- **Google service account JSON** (for Sheets queue management)
- **BlueSky app password** and/or **Mastodon access token** (for posting)

### 3. Register in Claude Code

Add to your `claude_desktop_config.json` (or Claude Code MCP settings):

```json
{
  "social-media": {
    "command": "python",
    "args": ["C:\\path\\to\\social-media-mcp\\src\\server.py"],
    "env": {
      "BLUESKY_HANDLE": "your.handle.bsky.social",
      "BLUESKY_APP_PASSWORD": "xxxx-xxxx-xxxx-xxxx",
      "MASTODON_INSTANCE": "https://mastodon.social",
      "MASTODON_ACCESS_TOKEN": "your_token",
      "OPENAI_API_KEY": "sk-...",
      "CONTENT_QUEUE_SHEET_ID": "your_sheet_id",
      "GOOGLE_CREDENTIALS_PATH": "C:\\path\\to\\service-account.json",
      "BRAND_VOICE_PATH": "C:\\path\\to\\brand_voice.json",
      "PYTHONIOENCODING": "utf-8"
    }
  }
}
```

### 4. Share the Google Sheet

Share your Content Queue spreadsheet with the service account email (found in your JSON key file).

## MCP Tools

| Tool | Description |
|------|-------------|
| `sm_create_content` | AI-generate platform-specific drafts from a topic |
| `sm_edit_draft` | Edit a draft in the queue |
| `sm_list_queue` | View queue items (filter by status) |
| `sm_approve` | Mark item as approved |
| `sm_schedule` | Set a publish time |
| `sm_post_now` | Post immediately to platforms |
| `sm_post_text` | Quick one-off post (no queue) |
| `sm_get_analytics` | View engagement analytics |
| `sm_refresh_analytics` | Fetch fresh metrics from APIs |
| `sm_list_accounts` | Show configured platforms |
| `sm_test_account` | Verify platform credentials |
| `sm_get_brand_voice` | View brand voice config |
| `sm_set_brand_voice` | Update brand voice |
| `sm_get_platform_status` | Live vs stub platforms |
| `sm_update_status` | Manual status change |

## Supported Platforms

| Platform | Status | Auth |
|----------|--------|------|
| BlueSky | Live | App Password |
| Mastodon | Live | Access Token |
| Facebook | Stub | Meta Graph API |
| Instagram | Stub | Meta Graph API |
| LinkedIn | Stub | OAuth 2.0 |
| X/Twitter | Stub | Excluded |

## Skills

Three SKILL.md files in `skills/` provide domain knowledge:

- **social-media-strategy** - Brand voice, platform guidelines, content pillars
- **social-media-posting** - MCP tool workflow guide
- **social-media-analytics** - Metrics interpretation for nonprofits

## Typical Workflow

```
1. sm_create_content("AI transparency in local government", "bluesky,mastodon")
   → AI generates platform-specific drafts, saved to queue

2. sm_list_queue(status="Draft")
   → Review drafts

3. sm_edit_draft(row=2, platform="bluesky", new_text="Updated text")
   → Edit if needed

4. sm_approve(queue_row=2)
   → Mark as approved

5. sm_post_now(queue_row=2)
   → Posts to all platforms with drafts
```

## Architecture

- **MCP Server**: FastMCP (Python) - handles interactive operations
- **Google Sheets**: Content queue and analytics storage
- **n8n Workflows**: Background automation (scheduled posting, analytics collection)
- **OpenAI**: Content generation with brand voice awareness
