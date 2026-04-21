from __future__ import annotations

from app.core.config import Settings
from app.services.audio_service import AudioService
from app.services.search_service import SearchService
from app.services.srs_service import SRSService
from app.services.translation_service import TranslationService
from app.services.vocabulary_store import VocabularyStore


class ServiceContainer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = VocabularyStore(settings.data_file)
        self.search = SearchService(self.store)
        self.srs = SRSService(self.store)
        self.translation = TranslationService()
        self.audio = AudioService(settings.audio_cache_dir, settings.tts_voice)

    def load(self) -> None:
        self.store.load()
