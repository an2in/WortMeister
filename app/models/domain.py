from __future__ import annotations

from dataclasses import dataclass, field


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


@dataclass(slots=True)
class MazePosition:
    row: int
    col: int


@dataclass(slots=True)
class MazeCell:
    row: int
    col: int
    kind: str
    letter: str = ""


@dataclass(slots=True)
class MazeSession:
    session_id: str
    target_word: str
    collected_letters: list[str] = field(default_factory=list)
    player_position: MazePosition = field(default_factory=lambda: MazePosition(row=0, col=0))
    cells: list[list[MazeCell]] = field(default_factory=list)
    letter_positions: list[MazePosition] = field(default_factory=list)
    status: str = "active"
    steps_taken: int = 0


@dataclass(slots=True)
class NotebookEntry:
    word: str
    meaning: str
    meaning_en: str = ""
    example: str = ""
    article: str = ""
    pos: str = "other"
    image_url: str = ""
    image_source: str = ""
    created_at: str = ""
