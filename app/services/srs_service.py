from __future__ import annotations

import datetime
import heapq
import time
from typing import Any

from fastapi import HTTPException

from app.models.domain import ReviewCard
from app.models.schemas import FlashcardResponse, UpdateCardRequest, UpdateCardResponse
from app.services.vocabulary_store import VocabularyStore


class SRSService:
    def __init__(self, store: VocabularyStore) -> None:
        self._store = store

    def get_next_card(self, lang: str) -> FlashcardResponse:
        if not self._store.srs_heap:
            raise HTTPException(status_code=404, detail="No cards available")

        _, word = heapq.heappop(self._store.srs_heap)
        entry = self._store.get_entry(word)
        if entry is None:
            raise HTTPException(status_code=404, detail=f"Word '{word}' not found")

        card = self._store.get_card(word)
        if card is None:
            raise HTTPException(status_code=404, detail=f"Card '{word}' not found")

        meaning = self._resolve_meaning(entry, lang)
        return FlashcardResponse(
            word=entry["word"],
            meaning=meaning,
            meaning_en=entry.get("meaning_en", ""),
            example=entry.get("example", ""),
            translation=entry.get("translation", ""),
            level=entry.get("level", ""),
            interval=card.interval,
            repetitions=card.repetitions,
            easiness=card.easiness,
            due=card.due,
        )

    def update_card(self, request: UpdateCardRequest) -> UpdateCardResponse:
        word = request.word.lower()
        card = self._store.get_card(word)
        if card is None:
            raise HTTPException(status_code=404, detail=f"Word '{request.word}' not in SRS")

        self._apply_sm2(card, request.quality)
        heapq.heappush(self._store.srs_heap, (card.due, word))

        due_str = datetime.datetime.fromtimestamp(card.due).strftime("%Y-%m-%d %H:%M")
        return UpdateCardResponse(
            success=True,
            word=request.word,
            new_interval=card.interval,
            new_due=due_str,
            message=f"Next review in {card.interval:.1f} day(s)",
        )

    @staticmethod
    def _resolve_meaning(entry: dict[str, Any], lang: str) -> str:
        if lang == "en" and entry.get("meaning_en"):
            return entry["meaning_en"]
        return entry["meaning"]

    @staticmethod
    def _apply_sm2(card: ReviewCard, quality: int) -> None:
        easiness = card.easiness
        repetitions = card.repetitions
        interval = card.interval

        easiness = max(1.3, easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

        if quality < 3:
            repetitions = 0
            interval = 1
        else:
            if repetitions == 0:
                interval = 1
            elif repetitions == 1:
                interval = 6
            else:
                interval = interval * easiness
            repetitions += 1

        card.easiness = round(easiness, 2)
        card.repetitions = repetitions
        card.interval = round(interval, 2)
        card.due = time.time() + interval * 86400
