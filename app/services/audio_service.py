from __future__ import annotations

import hashlib
from pathlib import Path

import edge_tts


class AudioService:
    def __init__(self, cache_dir: Path, voice: str) -> None:
        self._cache_dir = cache_dir
        self._voice = voice

    async def get_audio_path(self, word: str) -> Path:
        safe_hash = hashlib.md5(word.lower().encode("utf-8")).hexdigest()
        cache_path = self._cache_dir / f"{safe_hash}.mp3"

        if not cache_path.exists():
            try:
                communicator = edge_tts.Communicate(word, self._voice)
                await communicator.save(str(cache_path))
            except Exception as exc:
                raise RuntimeError(f"TTS generation failed: {exc}") from exc

        return cache_path
