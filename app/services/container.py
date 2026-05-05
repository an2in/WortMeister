from __future__ import annotations

from app.core.config import Settings
from app.services.article_drill_service import ArticleDrillService
from app.services.audio_service import AudioService
from app.services.context_analyzer_service import ContextAnalyzerService
from app.services.image_lookup_service import ImageLookupService
from app.services.maze_service import MazeService
from app.services.notebook_service import NotebookService
from app.services.notebook_store import NotebookStore
from app.services.pos_tagger_service import POSTaggerService
from app.services.search_service import SearchService
from app.services.srs_service import SRSService
from app.services.translation_service import TranslationService
from app.services.vocabulary_store import VocabularyStore


class ServiceContainer:
    """Assemble service graph and shared in-memory store."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = VocabularyStore(settings.data_file)
        self.notebook_store = NotebookStore(settings.notebook_data_file)

        self.search = SearchService(self.store)
        self.srs = SRSService(self.store)
        self.translation = TranslationService()
        self.audio = AudioService(settings.audio_cache_dir, settings.tts_voice)

        self.article_drill = ArticleDrillService(self.store)
        self.context_analyzer = ContextAnalyzerService(self.store)
        self.pos_tagger = POSTaggerService()
        self.image_lookup = ImageLookupService(settings)
        self.notebook = NotebookService(self.notebook_store, self.pos_tagger, self.image_lookup)
        self.maze = MazeService(settings.maze_default_size)

    def load(self) -> None:
        """Load persistent dataset into the in-memory store."""
        self.store.load()
        self.notebook_store.load()
