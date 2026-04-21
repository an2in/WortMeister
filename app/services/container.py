from __future__ import annotations

from app.core.config import Settings
from app.services.article_drill_service import ArticleDrillService
from app.services.audio_service import AudioService
from app.services.context_analyzer_service import ContextAnalyzerService
from app.services.search_service import SearchService
from app.services.srs_service import SRSService
from app.services.translation_service import TranslationService
from app.services.vocabulary_store import VocabularyStore


class ServiceContainer:
    """Assemble service graph and shared in-memory store."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = VocabularyStore(settings.data_file)

        self.search = SearchService(self.store)
        self.srs = SRSService(self.store)
        self.translation = TranslationService()
        self.audio = AudioService(settings.audio_cache_dir, settings.tts_voice)

        self.article_drill = ArticleDrillService(self.store)
        self.context_analyzer = ContextAnalyzerService(self.store)

    def load(self) -> None:
        """Load persistent dataset into the in-memory store."""
        self.store.load()
