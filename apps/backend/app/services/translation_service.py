from __future__ import annotations

from fastapi import HTTPException

from app.dsa.text_scan import contains_whole_word
from app.models.schemas import TranslationRequest, TranslationResponse


class TranslationService:
    def check_translation(self, request: TranslationRequest) -> TranslationResponse:
        target = request.target_word.strip()
        sentence = request.user_sentence.strip()

        if not target or not sentence:
            raise HTTPException(
                status_code=400,
                detail="Both target_word and user_sentence are required",
            )

        if contains_whole_word(sentence, target):
            return TranslationResponse(
                correct=True,
                target_word=target,
                feedback="Richtig!",
            )

        return TranslationResponse(
            correct=False,
            target_word=target,
            feedback="Versuche es nochmal!",
        )
