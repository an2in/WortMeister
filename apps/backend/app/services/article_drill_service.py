from __future__ import annotations

import heapq
import re
import time

from fastapi import HTTPException

from app.models.domain import DrillCard
from app.models.schemas import DrillAnswerRequest, DrillAnswerResponse, DrillQuestion
from app.services.vocabulary_store import VocabularyStore


class ArticleDrillService:
    """Manage reaction drills for German noun article and plural practice."""

    _ARTICLE_OPTIONS = ["der", "die", "das"]

    def __init__(self, store: VocabularyStore) -> None:
        self._store = store

    def get_next_question(self) -> DrillQuestion:
        """Return the next due noun for article/plural reaction training."""
        if not self._store.drill_heap:
            raise HTTPException(status_code=404, detail="No drill cards available")

        _, word = heapq.heappop(self._store.drill_heap)
        entry = self._store.get_entry(word)
        if entry is None:
            raise HTTPException(status_code=404, detail=f"Word '{word}' not found")

        expected_article = str(entry.get("article", "")).strip().lower()
        if expected_article not in self._ARTICLE_OPTIONS:
            raise HTTPException(status_code=404, detail=f"Word '{entry['word']}' is not drill-ready")

        plural_mode, expected_plural = self._resolve_plural(entry)

        card = self._store.get_drill_card(word)
        if card is None:
            raise HTTPException(status_code=404, detail=f"Drill card '{entry['word']}' not found")

        return DrillQuestion(
            word=entry["word"],
            article_options=self._ARTICLE_OPTIONS,
            attempts=card.attempts,
            mistakes=card.mistakes,
            hint=self._build_hint(plural_mode, expected_plural),
        )

    def submit_answer(self, request: DrillAnswerRequest) -> DrillAnswerResponse:
        """Evaluate user answer and reschedule noun by error frequency."""
        entry = self._store.get_entry(request.word)
        if entry is None:
            raise HTTPException(status_code=404, detail=f"Word '{request.word}' not found")

        word_key = entry["word"].lower()
        card = self._store.get_drill_card(word_key)
        if card is None:
            raise HTTPException(status_code=404, detail=f"Word '{request.word}' not in article drill")

        expected_article = str(entry.get("article", "")).strip().lower()
        plural_mode, expected_plural = self._resolve_plural(entry)

        article_answer = request.article.strip().lower()
        plural_answer = request.plural.strip()

        article_correct = article_answer == expected_article
        plural_correct = self._check_plural_answer(plural_mode, expected_plural, plural_answer)
        correct = article_correct and plural_correct

        self._update_schedule(card, correct)
        heapq.heappush(self._store.drill_heap, (card.due, word_key))

        next_due_in_minutes = max(0.0, (card.due - time.time()) / 60)
        message = "Richtig! Great reflex." if correct else "Incorrect. This noun will appear more frequently."

        return DrillAnswerResponse(
            word=entry["word"],
            article_correct=article_correct,
            plural_correct=plural_correct,
            correct=correct,
            expected_article=expected_article,
            expected_plural=self._display_plural(plural_mode, expected_plural),
            message=message,
            next_due_in_minutes=round(next_due_in_minutes, 2),
            attempts=card.attempts,
            mistakes=card.mistakes,
        )

    @staticmethod
    def _resolve_plural(entry: dict[str, object]) -> tuple[str, str]:
        """Resolve plural strategy from supported dataset keys."""
        for key in ("plural", "plural_form", "plural_de", "pl"):
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                return "exact", value.strip()

        word = str(entry.get("word", "")).strip()
        if not word:
            return "na", ""

        return "auto", ArticleDrillService._auto_plural(word)

    @staticmethod
    def _auto_plural(word: str) -> str:
        """Generate a simple plural guess when explicit data is unavailable."""
        lower = word.lower()
        if lower.endswith(("e", "el", "en", "er")):
            return word
        return f"{word}e"

    @staticmethod
    def _normalize_plural(value: str) -> str:
        """Normalize plural text for tolerant comparison."""
        compact = value.strip().lower()
        compact = re.sub(r"\s+", " ", compact)
        return compact

    @staticmethod
    def _check_plural_answer(mode: str, expected_plural: str, plural_answer: str) -> bool:
        """Validate plural answer using either exact or auto-derived mode."""
        if mode == "na":
            return True
        return ArticleDrillService._normalize_plural(plural_answer) == ArticleDrillService._normalize_plural(expected_plural)

    @staticmethod
    def _build_hint(mode: str, expected_plural: str) -> str:
        """Create user-facing hint for plural entry."""
        if mode == "na":
            return "Plural data unavailable for this noun."
        return f"Plural begins with: {expected_plural[:2]}..."

    @staticmethod
    def _display_plural(mode: str, expected_plural: str) -> str:
        """Format expected plural for response payload."""
        if mode == "na":
            return "N/A"
        if mode == "auto":
            return f"{expected_plural} (auto)"
        return expected_plural

    @staticmethod
    def _update_schedule(card: DrillCard, correct: bool) -> None:
        """Adjust drill interval with higher frequency for repeated mistakes."""
        card.attempts += 1

        if correct:
            card.streak += 1
            growth = 1.45 + min(card.streak, 5) * 0.1
            card.interval_minutes = min(60 * 24, max(5.0, card.interval_minutes * growth))
        else:
            card.streak = 0
            card.mistakes += 1
            penalty = min(card.mistakes, 6)
            card.interval_minutes = max(1.0, 6.0 - penalty)

        card.due = time.time() + card.interval_minutes * 60
