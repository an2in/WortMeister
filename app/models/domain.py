from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReviewCard:
    """SRS state for the classic flashcard flow (SM-2)."""

    interval: float = 0.0
    repetitions: int = 0
    easiness: float = 2.5
    due: float = 0.0


@dataclass(slots=True)
class DrillCard:
    """Scheduling state for article/plural reaction drills."""

    due: float = 0.0
    interval_minutes: float = 5.0
    streak: int = 0
    attempts: int = 0
    mistakes: int = 0
