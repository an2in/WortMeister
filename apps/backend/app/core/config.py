from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class Settings:
    data_file: Path
    audio_cache_dir: Path
    tts_voice: str
    notebook_data_file: Path
    user_state_dir: Path
    notebook_image_fallback: str
    notebook_image_lookup_enabled: bool
    notebook_image_lookup_timeout_seconds: float
    notebook_image_lookup_user_agent: str
    maze_default_size: int


settings = Settings(
    data_file=BASE_DIR / "data.json",
    audio_cache_dir=Path(tempfile.gettempdir()) / "wortmeister_audio",
    tts_voice="de-DE-ConradNeural",
    notebook_data_file=BASE_DIR / "notebook_data.json",
    user_state_dir=BASE_DIR / "user_state",
    notebook_image_fallback="",
    notebook_image_lookup_enabled=True,
    notebook_image_lookup_timeout_seconds=2.5,
    notebook_image_lookup_user_agent="WortMeister/0.1 (educational vocabulary notebook)",
    maze_default_size=9,
)

settings.audio_cache_dir.mkdir(parents=True, exist_ok=True)
