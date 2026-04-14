from __future__ import annotations

import heapq
import json
import time
from pathlib import Path
from typing import Any

from app.models.domain import ReviewCard


class VocabularyStore:
    def __init__(self, data_file: Path) -> None:
        self._data_file = data_file
        self.vocabulary: list[dict[str, Any]] = []
        self.sorted_words: list[str] = []
        self.word_index: dict[str, dict[str, Any]] = {}
        self.srs_heap: list[tuple[float, str]] = []
        self.srs_cards: dict[str, ReviewCard] = {}

    def load(self) -> None:
        if not self._data_file.exists():
            raise RuntimeError(f"Data file not found: {self._data_file}")

        with self._data_file.open("r", encoding="utf-8") as handle:
            raw_vocabulary = json.load(handle)

        if not isinstance(raw_vocabulary, list):
            raise RuntimeError("Vocabulary dataset must be a list of entries")

        self.vocabulary = sorted(raw_vocabulary, key=lambda entry: entry["word"].lower())
        self.sorted_words = []
        self.word_index = {}
        self.srs_heap = []
        self.srs_cards = {}

        now = time.time()
        for entry in self.vocabulary:
            normalized_word = entry["word"].lower()
            self.sorted_words.append(normalized_word)
            self.word_index[normalized_word] = entry

            card = ReviewCard(due=now)
            self.srs_cards[normalized_word] = card
            heapq.heappush(self.srs_heap, (card.due, normalized_word))

    def get_entry(self, word: str) -> dict[str, Any] | None:
        return self.word_index.get(word.lower())

    def get_card(self, word: str) -> ReviewCard | None:
        return self.srs_cards.get(word.lower())
