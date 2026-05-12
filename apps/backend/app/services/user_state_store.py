from __future__ import annotations

import datetime
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
        self._write_json(path, payload)

    def load_learning_progress(self, user_id: str) -> dict[str, Any]:
        path = self._learning_progress_path(user_id)
        if not path.exists():
            return self._build_learning_progress([])

        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        activity_dates = payload.get("activity_dates", []) if isinstance(payload, dict) else []
        return self._build_learning_progress(activity_dates)

    def record_learning_activity(self, user_id: str, activity_date: datetime.date | None = None) -> dict[str, Any]:
        path = self._learning_progress_path(user_id)
        progress = self.load_learning_progress(user_id)
        dates = set(progress["activity_dates"])
        dates.add((activity_date or datetime.date.today()).isoformat())
        progress = self._build_learning_progress(sorted(dates))
        payload = {
            "updated_at": time.time(),
            "activity_dates": progress["activity_dates"],
        }
        self._write_json(path, payload)
        return progress

    def _srs_state_path(self, user_id: str) -> Path:
        return self._user_dir(user_id) / "srs_state.json"

    def _learning_progress_path(self, user_id: str) -> Path:
        return self._user_dir(user_id) / "learning_progress.json"

    def _user_dir(self, user_id: str) -> Path:
        if not self._USER_ID_PATTERN.fullmatch(user_id):
            raise HTTPException(status_code=400, detail="Invalid user id")
        return self._state_dir / user_id

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(".tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        temp_path.replace(path)

    @staticmethod
    def _build_learning_progress(activity_dates: list[str]) -> dict[str, Any]:
        parsed_dates = sorted({datetime.date.fromisoformat(day) for day in activity_dates})
        today = datetime.date.today()
        activity_set = set(parsed_dates)

        current_streak = 0
        cursor = today
        while cursor in activity_set:
            current_streak += 1
            cursor -= datetime.timedelta(days=1)

        longest_streak = 0
        streak = 0
        previous: datetime.date | None = None
        for day in parsed_dates:
            if previous and day == previous + datetime.timedelta(days=1):
                streak += 1
            else:
                streak = 1
            longest_streak = max(longest_streak, streak)
            previous = day

        last_seven_days = [today - datetime.timedelta(days=offset) for offset in range(6, -1, -1)]
        return {
            "activity_dates": [day.isoformat() for day in parsed_dates],
            "current_streak_days": current_streak,
            "longest_streak_days": longest_streak,
            "last_activity_date": parsed_dates[-1].isoformat() if parsed_dates else None,
            "streak_last_7_days": [day in activity_set for day in last_seven_days],
        }
