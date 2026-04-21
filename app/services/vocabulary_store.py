from __future__ import annotations

import heapq
import json
import time
from pathlib import Path
from typing import Any

from app.models.domain import DrillCard, ReviewCard


class VocabularyStore:
    """In-memory vocabulary repository and scheduling state for learning flows."""

    def __init__(self, data_file: Path) -> None:
        self._data_file = data_file
        self.vocabulary: list[dict[str, Any]] = []
        self.sorted_words: list[str] = []
        self.word_index: dict[str, dict[str, Any]] = {}

        self.srs_heap: list[tuple[float, str]] = []
        self.srs_cards: dict[str, ReviewCard] = {}

        self.drill_heap: list[tuple[float, str]] = []
        self.drill_cards: dict[str, DrillCard] = {}

    def load(self) -> None:
        """Load vocabulary from JSON and initialize all scheduling structures."""
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

        self.drill_heap = []
        self.drill_cards = {}

        now = time.time()
        for entry in self.vocabulary:
            normalized_word = entry["word"].lower()
            self.sorted_words.append(normalized_word)
            self.word_index[normalized_word] = entry

            srs_card = ReviewCard(due=now)
            self.srs_cards[normalized_word] = srs_card
            heapq.heappush(self.srs_heap, (srs_card.due, normalized_word))

            article = str(entry.get("article", "")).strip().lower()
            if article in {"der", "die", "das"}:
                drill_card = DrillCard(due=now)
                self.drill_cards[normalized_word] = drill_card
                heapq.heappush(self.drill_heap, (drill_card.due, normalized_word))

    def get_entry(self, word: str) -> dict[str, Any] | None:
        """Return a vocabulary entry by normalized word key."""
        return self.word_index.get(word.lower())

    def get_card(self, word: str) -> ReviewCard | None:
        """Return SRS flashcard state for a word."""
        return self.srs_cards.get(word.lower())

    def get_drill_card(self, word: str) -> DrillCard | None:
        """Return article/plural drill scheduling state for a noun."""
        return self.drill_cards.get(word.lower())
