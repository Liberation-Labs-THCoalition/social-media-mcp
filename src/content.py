"""AI content generation using OpenAI."""

import json
from openai import AsyncOpenAI

import config
from models import Platform, PLATFORM_LIMITS


async def generate_content(
    topic: str,
    platforms: list[str],
    tone: str = "",
    org: str = "",
) -> dict[str, str]:
    """Generate platform-specific content drafts.

    Returns: {"bluesky": "draft text", "mastodon": "draft text", ...}
    """
    brand = config.get_brand_voice()
    org_name = org or brand.get("org_name", "our organization")
    voice_tone = tone or brand.get("tone", "professional but approachable")
    values = ", ".join(brand.get("values", []))
    avoid = ", ".join(brand.get("avoid", []))
    audience = brand.get("audience", "general public")

    platform_specs = []
    for p in platforms:
        try:
            plat = Platform(p)
            limit = PLATFORM_LIMITS.get(plat, 500)
            platform_specs.append(f"- {p}: max {limit} characters")
        except ValueError:
            platform_specs.append(f"- {p}: max 500 characters")

    system_prompt = f"""You are a social media content writer for {org_name}.

Brand Voice:
- Tone: {voice_tone}
- Values: {values}
- Avoid: {avoid}
- Audience: {audience}

Platform Guidelines:
- BlueSky: Casual, conversational, 300 char max, use hashtags sparingly
- Mastodon: Community-focused, can be longer (500 char), CW when appropriate
- LinkedIn: Professional, thought leadership, calls to action
- Facebook: Engagement-focused, questions work well, emoji acceptable
- Instagram: Visual-first, caption supports image, hashtags in comments

Generate a post for each requested platform. Each must respect the character limit.
Respond ONLY with valid JSON: {{"platform_name": "post text", ...}}
No markdown, no code fences, just the JSON object."""

    user_prompt = f"""Topic: {topic}
Platforms: {', '.join(platforms)}
Platform limits:
{chr(10).join(platform_specs)}"""

    client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )

    content = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    return json.loads(content)
