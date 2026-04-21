from __future__ import annotations

import hashlib
import re
from pathlib import Path

import edge_tts


class AudioService:
    """Generate and cache German pronunciation audio with Edge TTS."""

    def __init__(self, cache_dir: Path, voice: str) -> None:
        self._cache_dir = cache_dir
        self._voice = voice

    async def get_audio_path(self, word: str) -> Path:
        """Return cached audio path for a single vocabulary word."""
        normalized = self._normalize_text(word)
        return await self._get_or_create_audio(normalized)

    async def get_audio_path_for_text(self, text: str) -> Path:
        """Return cached audio path for arbitrary free-form German text."""
        normalized = self._normalize_text(text)
        return await self._get_or_create_audio(normalized)

    async def _get_or_create_audio(self, text: str) -> Path:
        """Generate MP3 on cache miss, otherwise reuse existing audio file."""
        safe_hash = hashlib.md5(text.lower().encode("utf-8")).hexdigest()
        cache_path = self._cache_dir / f"{safe_hash}.mp3"

        if not cache_path.exists():
            try:
                communicator = edge_tts.Communicate(text, self._voice)
                await communicator.save(str(cache_path))
            except Exception as exc:
                raise RuntimeError(f"TTS generation failed: {exc}") from exc

        return cache_path

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize user text before hashing and synthesis."""
        compact = re.sub(r"\s+", " ", text.strip())
        if not compact:
            raise RuntimeError("Text is required for TTS generation")
        return compact
