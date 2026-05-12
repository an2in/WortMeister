from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from fastapi import HTTPException

from app.models.schemas import (
    NotebookDeleteResponse,
    NotebookEntryPayload,
    NotebookGroup,
    NotebookGroupResponse,
    NotebookListResponse,
    NotebookUpsertRequest,
)
from app.services.image_lookup_service import ImageLookupService
from app.services.notebook_store import NotebookStore
from app.services.pos_tagger_service import POSTaggerService


class NotebookService:
    """Coordinate notebook CRUD, POS tagging, and illustration selection."""

    def __init__(
        self,
        store: NotebookStore,
        pos_tagger: POSTaggerService,
        image_lookup: ImageLookupService,
    ) -> None:
        self._store = store
        self._pos_tagger = pos_tagger
        self._image_lookup = image_lookup

    def list_entries(self, user_id: str, pos: str = "") -> NotebookListResponse:
        entries = [self._to_payload(entry) for entry in self._store.list_entries(user_id)]
        if pos.strip():
            entries = [entry for entry in entries if entry.pos == pos.strip().lower()]
        return NotebookListResponse(entries=entries)

    def grouped_entries(self, user_id: str) -> NotebookGroupResponse:
        buckets: dict[str, list[NotebookEntryPayload]] = {
            "noun": [],
            "verb": [],
            "adjective": [],
            "adverb": [],
            "other": [],
        }
        for entry in self.list_entries(user_id).entries:
            buckets.setdefault(entry.pos, []).append(entry)

        groups = [NotebookGroup(pos=pos, entries=entries) for pos, entries in buckets.items() if entries]
        return NotebookGroupResponse(groups=groups)

    def upsert_entry(self, user_id: str, request: NotebookUpsertRequest) -> NotebookEntryPayload:
        word = request.word.strip()
        if not word:
            raise HTTPException(status_code=400, detail="Word is required")

        article = request.article.strip().lower()
        if article and article not in {"der", "die", "das"}:
            raise HTTPException(status_code=400, detail="Article must be der, die, or das")

        pos = self._pos_tagger.detect(word, article)
        if pos == "noun" and not article and word[:1].isupper():
            raise HTTPException(status_code=400, detail="German nouns require an article in the notebook")

        existing = self._store.get_entry(user_id, word)
        created_at = existing.get("created_at") if existing else datetime.now(UTC).isoformat()
        image_url, image_source = self._image_lookup.resolve_image(word, request.image_url)

        entry: dict[str, Any] = {
            "word": word,
            "meaning": request.meaning.strip(),
            "meaning_en": request.meaning_en.strip(),
            "example": request.example.strip(),
            "article": article,
            "pos": pos,
            "image_url": image_url,
            "image_source": image_source,
            "created_at": created_at,
        }
        self._store.upsert_entry(user_id, entry)
        return self._to_payload(entry)

    def delete_entry(self, user_id: str, word: str) -> NotebookDeleteResponse:
        if not self._store.delete_entry(user_id, word):
            raise HTTPException(status_code=404, detail="Notebook word not found")
        return NotebookDeleteResponse(success=True, word=word)

    @staticmethod
    def _to_payload(entry: dict[str, Any]) -> NotebookEntryPayload:
        return NotebookEntryPayload(
            word=str(entry.get("word", "")),
            meaning=str(entry.get("meaning", "")),
            meaning_en=str(entry.get("meaning_en", "")),
            example=str(entry.get("example", "")),
            article=str(entry.get("article", "")),
            pos=str(entry.get("pos", "other")),
            image_url=str(entry.get("image_url", "")),
            image_source=str(entry.get("image_source", "")),
            created_at=str(entry.get("created_at", "")),
        )
