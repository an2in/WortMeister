from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class Settings:
    data_file: Path
    frontend_dir: Path
    audio_cache_dir: Path
    tts_voice: str


settings = Settings(
    data_file=BASE_DIR / "data.json",
    frontend_dir=BASE_DIR / "frontend",
    audio_cache_dir=Path(tempfile.gettempdir()) / "wortmeister_audio",
    tts_voice="de-DE-ConradNeural",
)

settings.audio_cache_dir.mkdir(parents=True, exist_ok=True)
