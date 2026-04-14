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
