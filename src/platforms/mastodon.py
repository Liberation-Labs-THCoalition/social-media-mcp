"""Mastodon platform client."""

from typing import Optional

import httpx

from platforms.base import BasePlatform
import config


class MastodonPlatform(BasePlatform):
    name = "mastodon"
    max_length = 500
    is_stub = False

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {config.MASTODON_ACCESS_TOKEN}"}

    def _url(self, path: str) -> str:
        return f"{config.MASTODON_INSTANCE.rstrip('/')}/api/v1{path}"

    async def post(self, text: str, media_urls: Optional[list[str]] = None) -> dict:
        text = self.truncate(text)
        media_ids = []

        async with httpx.AsyncClient() as http:
            # Upload media if provided
            if media_urls:
                for url in media_urls[:4]:
                    img_resp = await http.get(url)
                    upload_resp = await http.post(
                        self._url("/media"),
                        headers=self._headers(),
                        files={"file": ("image.jpg", img_resp.content, "image/jpeg")},
                    )
                    upload_resp.raise_for_status()
                    media_ids.append(upload_resp.json()["id"])

            # Create status
            payload = {"status": text}
            if media_ids:
                payload["media_ids"] = media_ids

            resp = await http.post(
                self._url("/statuses"),
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        return {
            "post_id": data["id"],
            "url": data["url"],
        }

    async def get_metrics(self, post_id: str) -> dict:
        async with httpx.AsyncClient() as http:
            try:
                resp = await http.get(
                    self._url(f"/statuses/{post_id}"),
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "likes": data.get("favourites_count", 0),
                    "reposts": data.get("reblogs_count", 0),
                    "replies": data.get("replies_count", 0),
                    "impressions": 0,  # Mastodon doesn't expose this
                }
            except Exception:
                return {"likes": 0, "reposts": 0, "replies": 0, "impressions": 0}

    async def verify_credentials(self) -> bool:
        try:
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    self._url("/accounts/verify_credentials"),
                    headers=self._headers(),
                )
                resp.raise_for_status()
                return True
        except Exception:
            return False
