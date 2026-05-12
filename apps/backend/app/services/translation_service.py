from __future__ import annotations

import re

from fastapi import HTTPException

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

        pattern = r"\b" + re.escape(target) + r"\b"
        match = re.search(pattern, sentence, re.IGNORECASE | re.UNICODE)

        if match:
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
