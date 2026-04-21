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
