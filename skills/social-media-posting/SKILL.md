---
name: social-media-posting
description: How to use the social-media MCP server tools to create, review, schedule, and publish posts. Use when you need to draft content, manage the posting queue, or publish to any platform.
---

# Social Media Posting Workflow

## Purpose

Step-by-step guide for using the social-media MCP tools to go from idea to published post. Covers the full workflow, quick posting, queue management, and common patterns.

## When to Use

- Creating and publishing social media posts
- Managing the content queue
- Setting up brand voice for content generation
- Batch-creating content for the week
- Running a campaign launch across platforms

## Full Workflow

The standard flow for quality content:

```
ideate --> sm_create_content --> review --> sm_edit_draft --> sm_approve --> sm_schedule or sm_post_now
```

### Step 1: Create Content

```
sm_create_content(
  org: "coalition",           # or "liberation-labs"
  platform: "bluesky",        # target platform
  topic: "New civic data toolkit launch",
  content_pillar: "civic-tech-in-action",
  tone: "excited-but-grounded"
)
```

This returns a draft with an ID. The draft respects the org's brand voice and the platform's character limits.

**Parameters:**
- `org` (required): Organization name
- `platform` (required): Target platform -- bluesky, mastodon, linkedin, facebook, instagram
- `topic` (required): What the post is about
- `content_pillar` (optional): Aligns to strategy pillars
- `tone` (optional): Override default tone
- `thread` (optional): Set `true` for multi-post threads
- `media_description` (optional): Describe accompanying images/video for alt text generation

### Step 2: Review the Draft

Read the returned draft. Check for:
- Brand voice alignment
- Accurate information
- Platform-appropriate length
- Clear call to action
- Hashtag count and placement

### Step 3: Edit if Needed

```
sm_edit_draft(
  draft_id: "abc123",
  changes: "Shorten the opening line. Remove the second hashtag. Add a question at the end."
)
```

You can also replace content directly:

```
sm_edit_draft(
  draft_id: "abc123",
  new_text: "Here's the exact text I want instead."
)
```

### Step 4: Approve

```
sm_approve(draft_id: "abc123")
```

This marks the draft as ready to publish. Nothing goes out without approval.

### Step 5: Schedule or Post

**Schedule for later:**
```
sm_schedule(
  draft_id: "abc123",
  datetime: "2026-02-03T10:00:00-05:00",
  timezone: "America/New_York"
)
```

**Post immediately:**
```
sm_post_now(draft_id: "abc123")
```

## Quick Posting

For simple one-off posts that don't need the full pipeline:

```
sm_post_text(
  account: "coalition-bluesky",
  text: "We just open-sourced our voter data toolkit. Civic infrastructure belongs to everyone. github.com/coalition/voter-toolkit",
  hashtags: ["CivicTech"]
)
```

Use quick posting for:
- Time-sensitive responses
- Simple announcements
- Boosting/amplifying others' content
- Event live-posting

Do NOT use quick posting for:
- Campaign content
- Anything controversial or sensitive
- Content that represents a policy position
- Posts with complex media attachments

## Queue Management

### View the Queue

```
sm_list_queue(
  org: "coalition",
  status: "scheduled",       # draft, approved, scheduled, published, failed
  platform: "all",
  date_range: "this-week"
)
```

### Update a Queued Post

```
sm_update_status(
  draft_id: "abc123",
  status: "draft",           # pull back from scheduled to draft
  reason: "Need to update the link"
)
```

**Status transitions:**
- `draft` --> `approved` --> `scheduled` --> `published`
- Any status --> `draft` (pull back for editing)
- Any status --> `cancelled`
- `failed` --> `draft` (retry after fixing)

### Check What Published

```
sm_list_queue(
  org: "coalition",
  status: "published",
  date_range: "today"
)
```

## Brand Voice Configuration

### View Current Voice Settings

```
sm_get_brand_voice(org: "coalition")
```

Returns the configured voice profile: tone descriptors, vocabulary preferences, example posts, and constraints.

### Update Voice Settings

```
sm_set_brand_voice(
  org: "coalition",
  voice: {
    tone: ["warm", "direct", "optimistic", "grounded"],
    avoid: ["jargon", "corporate-speak", "fear-based"],
    vocabulary: ["community", "together", "open", "accessible"],
    example_posts: ["We build tools for civic power. All open source, all free."]
  }
)
```

Update the voice profile when:
- Launching a new campaign with a distinct tone
- Onboarding and setting up for the first time
- Refining based on what's resonating with the audience

## Account Setup

### List Connected Accounts

```
sm_list_accounts(org: "coalition")
```

Returns all connected platform accounts with status and permissions.

### Test a Connection

```
sm_test_account(account: "coalition-bluesky")
```

Run this before a big posting session to confirm API connections are live. Returns connection status, rate limit remaining, and last successful post timestamp.

## Common Patterns

### Batch Content Creation (Weekly Planning)

Create a week of content in one session:

1. `sm_get_brand_voice(org: "coalition")` -- load context
2. For each day, run `sm_create_content` with that day's topic and pillar
3. Review all drafts together for variety and flow
4. Edit as needed with `sm_edit_draft`
5. Approve all with `sm_approve`
6. Schedule each with `sm_schedule` at optimal times

**Optimal posting times (Eastern):**
- BlueSky: 9-10 AM, 1-2 PM
- Mastodon: 8-9 AM, 5-6 PM
- LinkedIn: 8-10 AM Tuesday-Thursday
- Facebook: 10 AM - 12 PM
- Instagram: 11 AM - 1 PM, 7-8 PM

### Campaign Launch (Multi-Platform)

Roll out an announcement across all platforms at once:

1. Create platform-specific versions of the same announcement:
   ```
   sm_create_content(org: "coalition", platform: "bluesky", topic: "Toolkit v2 launch")
   sm_create_content(org: "coalition", platform: "mastodon", topic: "Toolkit v2 launch")
   sm_create_content(org: "coalition", platform: "linkedin", topic: "Toolkit v2 launch")
   ```
2. Each draft will be tailored to the platform's format and audience
3. Review, edit, approve each
4. Schedule all for the same launch window, or stagger by 15-30 minutes

### Event Promotion

**2 weeks out:**
- Announcement post across all platforms
- Create event on Facebook if applicable

**1 week out:**
- Speaker/topic spotlight posts
- "Save the date" reminder

**Day before:**
- "Tomorrow!" reminder with logistics

**Day of:**
- Use `sm_post_text` for live updates
- Stories on Instagram
- Thread on BlueSky/Mastodon

**Day after:**
- Recap with photos/highlights
- Thank-you post tagging participants

## Error Handling

### Common Errors and Fixes

**"Character limit exceeded"**
- The draft is too long for the target platform. Run `sm_edit_draft` with instruction to shorten, or split into a thread.

**"Account connection failed"**
- Run `sm_test_account` to diagnose. Usually an expired token. Reconnect via the account settings.

**"Rate limit reached"**
- Wait and retry. Most platforms reset rate limits hourly. Check `sm_test_account` for remaining quota.

**"Draft not found"**
- Draft IDs expire after 30 days. If working with old content, recreate with `sm_create_content`.

**"Scheduling failed"**
- Check that the datetime is in the future and the timezone is valid. Use ISO 8601 format.

**"Post failed"**
- Check `sm_list_queue(status: "failed")` for details. Common causes: deleted account, API changes, content policy flags. Fix the issue and update status back to `draft` to retry.

### Pre-Flight Checklist

Before any important post:
1. `sm_test_account` -- confirm connection is live
2. `sm_get_brand_voice` -- confirm voice is set correctly
3. Review draft for typos, broken links, correct handles
4. Check the queue for conflicts -- don't double-post on the same topic
5. Approve and schedule (or post)
