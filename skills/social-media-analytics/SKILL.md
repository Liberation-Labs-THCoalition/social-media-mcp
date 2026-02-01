---
name: social-media-analytics
description: Interpreting social media analytics for nonprofit audiences. Use when reviewing performance, building reports, adjusting strategy based on data, or understanding what's working.
---

# Social Media Analytics for Nonprofits

## Purpose

Help nonprofits understand what their social media numbers actually mean and what to do about them. Focuses on metrics that matter for mission-driven organizations, not vanity metrics.

## When to Use

- Reviewing weekly or monthly performance
- Deciding what content to make more (or less) of
- Building reports for leadership or board
- Comparing performance across platforms
- Justifying social media time investment

## Metrics That Matter for Nonprofits

### Tier 1: Prioritize These

| Metric | Why It Matters | What to Track |
|--------|---------------|---------------|
| **Engagement rate** | Shows your content resonates, not just that people saw it | (Likes + comments + shares) / impressions |
| **Shares / reposts** | Each share extends reach to new audiences for free | Share count per post |
| **Link clicks** | People took action -- visited your site, signed up, donated | Click-through rate (clicks / impressions) |
| **Comments** | Real conversation signals deep engagement | Comment count and sentiment |
| **Follower growth rate** | Growth trajectory matters more than total count | New followers per week as % of total |

### Tier 2: Useful Context

| Metric | Why It Matters |
|--------|---------------|
| Impressions | How many eyeballs saw it (but seeing is not engaging) |
| Reach | Unique people who saw it (deduped impressions) |
| Profile visits | Curiosity signal -- people wanted to know more about you |
| Save / bookmark rate | Content people want to come back to (high value) |

### Tier 3: Ignore or Deprioritize

| Metric | Why to Ignore |
|--------|--------------|
| Total follower count (raw number) | Says nothing about engagement or impact |
| Likes alone | Lowest-effort interaction, weakest signal |
| Impressions without engagement context | Big numbers that mean little |
| Follower count comparisons to large orgs | Different scale, different game |

## Using the Analytics Tools

### Pull Analytics

```
sm_get_analytics(
  account: "coalition-bluesky",
  period: "last-7-days",
  metrics: ["engagement_rate", "shares", "link_clicks", "follower_growth"]
)
```

**Parameters:**
- `account` (required): Which account to analyze
- `period`: last-7-days, last-30-days, last-quarter, custom date range
- `metrics`: Specific metrics to pull. Omit for all available.
- `compare_to`: "previous-period" for trend comparison

### Refresh Data

```
sm_refresh_analytics(account: "coalition-bluesky")
```

Run this before pulling analytics if you need the most current numbers. Platform APIs sometimes lag by a few hours.

### Cross-Platform Comparison

```
sm_get_analytics(
  org: "coalition",
  period: "last-30-days",
  group_by: "platform"
)
```

Returns a side-by-side comparison across all connected accounts for the org.

## Performance Benchmarks

### What "Good" Looks Like for Small Nonprofits

These benchmarks are for organizations with under 10,000 followers per platform.

| Metric | Poor | Acceptable | Good | Excellent |
|--------|------|-----------|------|-----------|
| **Engagement rate** | < 0.5% | 0.5-1% | 1-3% | 3-5%+ |
| **Link CTR** | < 0.3% | 0.3-0.7% | 0.7-1.5% | 1.5%+ |
| **Follower growth (weekly)** | < 0.1% | 0.1-0.5% | 0.5-1.5% | 1.5%+ |
| **Share rate** | < 0.1% | 0.1-0.5% | 0.5-1% | 1%+ |

**Important context:** A 200-follower account with 5% engagement is outperforming a 50,000-follower account with 0.2% engagement in every way that matters for a nonprofit.

### Platform-Specific Benchmarks

**BlueSky**
- Still growing as a platform. Engagement rates tend to be higher (2-5%) because feeds are more chronological.
- Repost rate is a key health metric here.

**Mastodon**
- Highly engaged but smaller audiences. Expect 3-8% engagement rates.
- Boosts (shares) are the primary growth mechanism. Track boost rate closely.
- Follower counts grow slowly. This is normal.

**LinkedIn**
- Engagement rates of 1-3% are solid for nonprofit pages.
- Comments are weighted heavily by the algorithm. A post with 5 comments outperforms one with 50 likes.
- Document/carousel posts consistently outperform text-only.

**Facebook**
- Organic reach is low (2-6% of followers see any given post).
- Video and photo posts get 2-3x the reach of text/link posts.
- Comments and shares are the only engagement signals that meaningfully boost distribution.

**Instagram**
- Reels reach 2-5x more non-followers than static posts.
- Carousel posts get the highest engagement rate (saves + shares).
- Stories maintain daily connection but don't grow audience.

## Weekly Report Template

Run this every Monday to assess the previous week:

### Step 1: Pull the Data

```
sm_get_analytics(
  org: "coalition",
  period: "last-7-days",
  compare_to: "previous-period"
)
```

### Step 2: Build the Report

**Week of [DATE] -- Social Media Summary**

**Top-line numbers:**
- Total posts published: X
- Total engagements: X (up/down Y% from last week)
- Average engagement rate: X%
- New followers: X across all platforms
- Link clicks: X

**Top performing post:**
- Platform: [which]
- Content: [summary]
- Engagement rate: X%
- Why it worked: [brief analysis]

**Worst performing post:**
- Platform: [which]
- Content: [summary]
- Engagement rate: X%
- What to learn: [brief analysis]

**Key takeaways:**
- [1 sentence on what content type is working]
- [1 sentence on which platform is growing]
- [1 sentence on what to try next week]

### Step 3: Adjust

Based on the report, update next week's content plan:
- More of what's working (double down on high-performing content types)
- Less of what's not (drop or rework underperforming formats)
- One experiment (try something new each week)

## Monthly Report Template

Run at the start of each month for the previous month:

```
sm_get_analytics(
  org: "coalition",
  period: "last-30-days",
  compare_to: "previous-period",
  metrics: ["engagement_rate", "follower_growth", "shares", "link_clicks", "top_posts"]
)
```

**Month of [MONTH] -- Social Media Report**

**Summary:**
- Posts published: X (target: Y)
- Average engagement rate: X% (benchmark: 1-3%)
- Follower growth: +X (Y% increase)
- Total link clicks: X
- Top platform by engagement: [which]

**Content performance by pillar:**

| Pillar | Posts | Avg Engagement Rate | Best Post |
|--------|-------|-------------------|-----------|
| Civic tech in action | X | X% | [title] |
| Community voices | X | X% | [title] |
| Open source ethos | X | X% | [title] |
| Policy and rights | X | X% | [title] |
| Behind the scenes | X | X% | [title] |

**Platform breakdown:**

| Platform | Followers | Growth | Engagement Rate | Top Post |
|----------|-----------|--------|----------------|----------|
| BlueSky | X | +X% | X% | [title] |
| Mastodon | X | +X% | X% | [title] |
| LinkedIn | X | +X% | X% | [title] |

**Recommendations for next month:**
1. [Strategy adjustment based on data]
2. [Content type to prioritize]
3. [Platform-specific action item]

## Interpreting Trends

### Engagement Rate Dropping

**Possible causes:**
- Posting too frequently (audience fatigue)
- Content is too similar week to week
- Shift in platform algorithm
- Audience has grown but new followers are less engaged

**What to do:**
- Pull per-post analytics to find which posts dragged the average down
- Compare content types -- are certain formats underperforming?
- Reduce posting frequency for 2 weeks and measure impact
- Run an engagement-focused post (question, poll, discussion prompt)

### Follower Growth Stalled

**Possible causes:**
- Not enough shareable content (shares bring new followers)
- Posting at low-visibility times
- Content is engaging existing audience but not reaching new people
- No cross-promotion or collaboration happening

**What to do:**
- Increase share-worthy content (data, insights, strong opinions, resources)
- Collaborate with aligned orgs for mutual amplification
- Try one piece of content specifically designed for virality (thread, carousel, hot take)
- Cross-promote accounts across platforms

### High Impressions, Low Engagement

**Possible causes:**
- Content is seen but not compelling enough to interact with
- Posts lack a clear call to action
- Audience mismatch -- reaching people outside your target

**What to do:**
- Add explicit engagement hooks: questions, polls, "what do you think?"
- Test shorter, punchier posts vs. longer educational ones
- Review who is seeing the content (if platform provides demographic data)

## Avoiding Vanity Metrics

**Do not report these to leadership as success indicators:**
- "We reached 1,000 followers!" (without engagement context)
- "This post got 10,000 impressions!" (without engagement rate)
- "We posted 25 times this month!" (activity is not impact)

**Instead, report:**
- "Our engagement rate grew from 1.2% to 2.4% this month"
- "Our toolkit launch post was shared 85 times, reaching an estimated 3,000 new people"
- "Link clicks to our donation page increased 40% after we shifted to storytelling posts"

The question leadership actually cares about: **Is our social media presence helping us advance our mission?** Frame every metric in terms of whether it moves the needle on awareness, engagement, action, or community building.
