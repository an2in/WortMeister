from __future__ import annotations

import json
import urllib.parse
import urllib.request

from app.core.config import Settings


class ImageLookupService:
    """Resolve a notebook illustration URL for a vocabulary entry."""

    _RASTER_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def resolve_image(self, word: str, provided_url: str = "") -> tuple[str, str]:
        image_url = provided_url.strip()
        if image_url:
            return image_url, "user"

        if self._settings.notebook_image_lookup_enabled:
            lookup_url = self._lookup_wikimedia(word)
            if lookup_url:
                return lookup_url, "wikimedia"

        fallback = self._settings.notebook_image_fallback.format(word=urllib.parse.quote(word.strip()))
        return fallback, "fallback"

    def _lookup_wikimedia(self, word: str) -> str:
        query = word.strip()
        if not query:
            return ""

        params = urllib.parse.urlencode(
            {
                "action": "query",
                "format": "json",
                "generator": "search",
                "gsrnamespace": "6",
                "gsrsearch": f"{query} filetype:bitmap",
                "gsrlimit": "8",
                "prop": "imageinfo",
                "iiprop": "url|mime",
                "origin": "*",
            }
        )
        request = urllib.request.Request(
            f"https://commons.wikimedia.org/w/api.php?{params}",
            headers={"User-Agent": self._settings.notebook_image_lookup_user_agent},
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self._settings.notebook_image_lookup_timeout_seconds,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            return ""

        pages = payload.get("query", {}).get("pages", {}) if isinstance(payload, dict) else {}
        if not isinstance(pages, dict):
            return ""

        for page in pages.values():
            image_info = page.get("imageinfo", []) if isinstance(page, dict) else []
            if not image_info or not isinstance(image_info[0], dict):
                continue
            url = str(image_info[0].get("url", ""))
            mime = str(image_info[0].get("mime", ""))
            if self._is_supported_image(url, mime):
                return url
        return ""

    def _is_supported_image(self, url: str, mime: str) -> bool:
        parsed_path = urllib.parse.urlparse(url).path.lower()
        return mime in {"image/jpeg", "image/png", "image/webp"} or parsed_path.endswith(self._RASTER_EXTENSIONS)
