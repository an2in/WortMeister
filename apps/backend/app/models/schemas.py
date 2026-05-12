from __future__ import annotations

from pydantic import BaseModel, Field


class WordEntry(BaseModel):
    word: str
    meaning: str
    meaning_en: str = ""
    example: str
    translation: str
    level: str


class SearchResponse(BaseModel):
    results: list[WordEntry]


class FlashcardResponse(BaseModel):
    word: str
    meaning: str
    meaning_en: str = ""
    example: str
    translation: str
    level: str
    interval: float = Field(description="Current review interval in days")
    repetitions: int = Field(description="Number of successful reviews")
    easiness: float = Field(description="Easiness factor (SM-2)")
    due: float = Field(description="Unix timestamp when card is due")


class UpdateCardRequest(BaseModel):
    word: str
    quality: int = Field(ge=0, le=5, description="Review quality 0-5 (SM-2 scale)")


class UpdateCardResponse(BaseModel):
    success: bool
    word: str
    new_interval: float
    new_due: str
    message: str


class SRSStatsResponse(BaseModel):
    total_cards: int
    due_cards: int
    learned_cards: int
    next_due: float | None = None


class TranslationRequest(BaseModel):
    target_word: str = Field(description="The German word the user is practising")
    user_sentence: str = Field(description="User's German sentence")


class TranslationResponse(BaseModel):
    correct: bool
    target_word: str
    feedback: str


class DrillQuestion(BaseModel):
    """Question payload for article/plural reaction drill."""

    word: str
    article_options: list[str]
    attempts: int
    mistakes: int
    hint: str


class DrillAnswerRequest(BaseModel):
    """User answer for article/plural reaction drill."""

    word: str
    article: str = Field(description="Chosen article: der/die/das")
    plural: str = Field(default="", description="User-provided plural form")


class DrillAnswerResponse(BaseModel):
    """Result after evaluating a drill answer and updating schedule."""

    word: str
    article_correct: bool
    plural_correct: bool
    correct: bool
    expected_article: str
    expected_plural: str
    message: str
    next_due_in_minutes: float
    attempts: int
    mistakes: int


class ContextAnalyzeRequest(BaseModel):
    """Request payload for context analyzer."""

    text: str = Field(min_length=1, description="German text to analyze")
    lang: str = Field(default="vi", description="Meaning language: vi or en")


class ContextToken(BaseModel):
    """A matched token found in user-provided context text."""

    word: str
    start: int
    end: int
    meaning: str
    meaning_en: str = ""
    example: str = ""
    article: str = ""


class ContextAnalyzeResponse(BaseModel):
    """Context analyzer output with matched vocabulary metadata."""

    text: str
    matches: list[ContextToken]


class FreeTTSRequest(BaseModel):
    """Request payload for free-form text-to-speech."""

    text: str = Field(min_length=1, description="German text to synthesize")


class FreeTTSResponse(BaseModel):
    """Response containing playable URL for synthesized free-form text."""

    text: str
    audio_url: str


class MazePositionPayload(BaseModel):
    row: int
    col: int


class MazeCellPayload(BaseModel):
    row: int
    col: int
    kind: str
    letter: str = ""


class MazeStartRequest(BaseModel):
    target_word: str = Field(min_length=1)


class MazeSessionResponse(BaseModel):
    session_id: str
    target_word: str
    collected_letters: list[str]
    remaining_letters: list[str]
    player_position: MazePositionPayload
    cells: list[list[MazeCellPayload]]
    status: str
    steps_taken: int
    shortest_goal_distance: int | None = None


class MazeMoveRequest(BaseModel):
    direction: str


class MazeMoveResponse(BaseModel):
    moved: bool
    hit_wall: bool
    collected_letter: str
    completed: bool
    state: MazeSessionResponse


class NotebookUpsertRequest(BaseModel):
    word: str = Field(min_length=1)
    meaning: str = Field(min_length=1)
    meaning_en: str = ""
    example: str = ""
    article: str = ""
    image_url: str = ""


class NotebookEntryPayload(BaseModel):
    word: str
    meaning: str
    meaning_en: str = ""
    example: str = ""
    article: str = ""
    pos: str
    image_url: str
    image_source: str
    created_at: str


class NotebookListResponse(BaseModel):
    entries: list[NotebookEntryPayload]


class NotebookGroup(BaseModel):
    pos: str
    entries: list[NotebookEntryPayload]


class NotebookGroupResponse(BaseModel):
    groups: list[NotebookGroup]


class NotebookDeleteResponse(BaseModel):
    success: bool
    word: str
