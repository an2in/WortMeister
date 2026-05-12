from __future__ import annotations

import bisect
from typing import Any

from app.models.schemas import SearchResponse, WordEntry
from app.services.vocabulary_store import VocabularyStore


class SearchService:
    def __init__(self, store: VocabularyStore) -> None:
        self._store = store

    def search(self, query: str, lang: str) -> SearchResponse:
        prefix = query.strip().lower()
        if not prefix:
            return SearchResponse(results=[])

        index = bisect.bisect_left(self._store.sorted_words, prefix)
        results: list[WordEntry] = []

        while (
            index < len(self._store.sorted_words)
            and self._store.sorted_words[index].startswith(prefix)
            and len(results) < 10
        ):
            entry = self._store.word_index[self._store.sorted_words[index]]
            results.append(self._build_word_entry(entry, lang))
            index += 1

        return SearchResponse(results=results)

    @staticmethod
    def _build_word_entry(entry: dict[str, Any], lang: str) -> WordEntry:
        meaning = entry["meaning_en"] if lang == "en" and entry.get("meaning_en") else entry["meaning"]
        return WordEntry(
            word=entry["word"],
            meaning=meaning,
            meaning_en=entry.get("meaning_en", ""),
            example=entry.get("example", ""),
            translation=entry.get("translation", ""),
            level=entry.get("level", ""),
        )
