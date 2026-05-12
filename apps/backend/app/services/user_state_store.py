from __future__ import annotations

import json
import re
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from app.models.domain import ReviewCard


class UserStateStore:
    _USER_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")

    def __init__(self, state_dir: Path) -> None:
        self._state_dir = state_dir

    def load_srs_cards(self, user_id: str, vocabulary: list[dict[str, Any]]) -> dict[str, ReviewCard]:
        path = self._srs_state_path(user_id)
        vocabulary_keys = {entry["word"].lower() for entry in vocabulary}
        cards: dict[str, ReviewCard] = {}

        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            raw_cards = payload.get("cards", {}) if isinstance(payload, dict) else {}
            for word, raw_card in raw_cards.items():
                normalized_word = word.lower()
                if normalized_word not in vocabulary_keys or not isinstance(raw_card, dict):
                    continue
                cards[normalized_word] = ReviewCard(
                    interval=float(raw_card.get("interval", 0.0)),
                    repetitions=int(raw_card.get("repetitions", 0)),
                    easiness=float(raw_card.get("easiness", 2.5)),
                    due=float(raw_card.get("due", 0.0)),
                )

        now = time.time()
        for word in vocabulary_keys:
            cards.setdefault(word, ReviewCard(due=now))

        return cards

    def save_srs_cards(self, user_id: str, cards: dict[str, ReviewCard]) -> None:
        path = self._srs_state_path(user_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "updated_at": time.time(),
            "cards": {word: asdict(card) for word, card in sorted(cards.items())},
        }
        temp_path = path.with_suffix(".tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        temp_path.replace(path)

    def _srs_state_path(self, user_id: str) -> Path:
        if not self._USER_ID_PATTERN.fullmatch(user_id):
            raise HTTPException(status_code=400, detail="Invalid user id")
        return self._state_dir / user_id / "srs_state.json"
