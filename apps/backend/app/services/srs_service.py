from __future__ import annotations

import datetime
import time
from typing import Any

from fastapi import HTTPException

from app.dsa.heap import MinHeap
from app.models.domain import ReviewCard
from app.models.schemas import FlashcardResponse, SRSStatsResponse, UpdateCardRequest, UpdateCardResponse
from app.services.user_state_store import UserStateStore
from app.services.vocabulary_store import VocabularyStore


class SRSService:
    def __init__(self, store: VocabularyStore, user_state_store: UserStateStore) -> None:
        self._store = store
        self._user_state_store = user_state_store

    def get_stats(self, user_id: str) -> SRSStatsResponse:
        cards = self._load_user_cards(user_id)
        progress = self._user_state_store.load_learning_progress(user_id)
        now = time.time()
        due_times = [card.due for card in cards.values()]
        next_due = min(due_times) if due_times else None
        return SRSStatsResponse(
            total_cards=len(cards),
            due_cards=sum(1 for card in cards.values() if card.due <= now),
            learned_cards=sum(1 for card in cards.values() if card.repetitions > 2),
            next_due=next_due,
            current_streak_days=progress["current_streak_days"],
            longest_streak_days=progress["longest_streak_days"],
            last_activity_date=progress["last_activity_date"],
            streak_last_7_days=progress["streak_last_7_days"],
        )

    def get_next_card(self, user_id: str, lang: str) -> FlashcardResponse:
        cards = self._load_user_cards(user_id)
        heap = self._build_heap(cards)
        if not heap:
            raise HTTPException(status_code=404, detail="No cards available")

        due, word = heap.pop()
        if due > time.time():
            raise HTTPException(status_code=404, detail="No cards due")

        entry = self._store.get_entry(word)
        if entry is None:
            raise HTTPException(status_code=404, detail=f"Word '{word}' not found")

        card = cards.get(word)
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

    def update_card(self, user_id: str, request: UpdateCardRequest) -> UpdateCardResponse:
        cards = self._load_user_cards(user_id)
        word = request.word.lower()
        card = cards.get(word)
        if card is None:
            raise HTTPException(status_code=404, detail=f"Word '{request.word}' not in SRS")

        self._apply_sm2(card, request.quality)
        self._user_state_store.save_srs_cards(user_id, cards)
        self._user_state_store.record_learning_activity(user_id)

        due_str = datetime.datetime.fromtimestamp(card.due).strftime("%Y-%m-%d %H:%M")
        return UpdateCardResponse(
            success=True,
            word=request.word,
            new_interval=card.interval,
            new_due=due_str,
            message=f"Next review in {card.interval:.1f} day(s)",
        )

    def _load_user_cards(self, user_id: str) -> dict[str, ReviewCard]:
        return self._user_state_store.load_srs_cards(user_id, self._store.vocabulary)

    @staticmethod
    def _build_heap(cards: dict[str, ReviewCard]) -> MinHeap[tuple[float, str]]:
        return MinHeap([(card.due, word) for word, card in cards.items()])

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
