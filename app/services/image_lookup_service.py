from __future__ import annotations

from app.core.config import Settings


class ImageLookupService:
    """Resolve a notebook illustration URL for a vocabulary entry."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def resolve_image(self, word: str, provided_url: str = "") -> tuple[str, str]:
        image_url = provided_url.strip()
        if image_url:
            return image_url, "user"
        return self._settings.notebook_image_fallback.format(word=word.strip()), "fallback"
