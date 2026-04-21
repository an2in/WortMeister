from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReviewCard:
    interval: float = 0.0
    repetitions: int = 0
    easiness: float = 2.5
    due: float = 0.0
