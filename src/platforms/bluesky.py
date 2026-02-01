"""BlueSky (AT Protocol) platform client."""

from typing import Optional

from platforms.base import BasePlatform
import config


class BlueSkyPlatform(BasePlatform):
    name = "bluesky"
    max_length = 300
    is_stub = False

    def __init__(self):
        self._client = None

    async def _get_client(self):
        if self._client is None:
            from atproto import AsyncClient
            self._client = AsyncClient()
            await self._client.login(config.BLUESKY_HANDLE, config.BLUESKY_APP_PASSWORD)
        return self._client

    async def post(self, text: str, media_urls: Optional[list[str]] = None) -> dict:
        client = await self._get_client()
        text = self.truncate(text)

        if media_urls:
            # Upload images and create embed
            import httpx
            images = []
            async with httpx.AsyncClient() as http:
                for url in media_urls[:4]:  # BlueSky max 4 images
                    resp = await http.get(url)
                    upload = await client.upload_blob(resp.content)
                    images.append({"alt": "", "image": upload.blob})

            from atproto import models as atmodels
            embed = atmodels.AppBskyEmbedImages.Main(images=[
                atmodels.AppBskyEmbedImages.Image(alt=img["alt"], image=img["image"])
                for img in images
            ])
            response = await client.send_post(text=text, embed=embed)
        else:
            response = await client.send_post(text=text)

        # Extract post URI and construct URL
        post_uri = response.uri
        # URI format: at://did:plc:xxx/app.bsky.feed.post/rkey
        parts = post_uri.split("/")
        rkey = parts[-1]
        handle = config.BLUESKY_HANDLE

        return {
            "post_id": post_uri,
            "url": f"https://bsky.app/profile/{handle}/post/{rkey}",
        }

    async def get_metrics(self, post_id: str) -> dict:
        client = await self._get_client()
        try:
            from atproto import models as atmodels
            # Get thread to access metrics
            response = await client.get_post_thread(uri=post_id)
            post = response.thread.post
            return {
                "likes": post.like_count or 0,
                "reposts": post.repost_count or 0,
                "replies": post.reply_count or 0,
                "impressions": 0,  # BlueSky doesn't expose impressions
            }
        except Exception:
            return {"likes": 0, "reposts": 0, "replies": 0, "impressions": 0}

    async def verify_credentials(self) -> bool:
        try:
            client = await self._get_client()
            profile = await client.get_profile(config.BLUESKY_HANDLE)
            return bool(profile.did)
        except Exception:
            return False
