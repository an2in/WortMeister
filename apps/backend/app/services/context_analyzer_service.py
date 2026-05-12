from __future__ import annotations

import re
from typing import Any

from fastapi import HTTPException

from app.models.schemas import ContextAnalyzeRequest, ContextAnalyzeResponse, ContextToken
from app.services.vocabulary_store import VocabularyStore


class ContextAnalyzerService:
    """Analyze custom German text and locate known vocabulary in context."""

    _TOKEN_PATTERN = re.compile(r"[A-Za-zÄÖÜäöüß-]+", re.UNICODE)

    def __init__(self, store: VocabularyStore) -> None:
        self._store = store

    def analyze(self, request: ContextAnalyzeRequest) -> ContextAnalyzeResponse:
        """Return token matches with metadata for inline highlighting."""
        text = request.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        matches = self._collect_matches(text, request.lang)
        return ContextAnalyzeResponse(text=text, matches=matches)

    def _collect_matches(self, text: str, lang: str) -> list[ContextToken]:
        """Collect unique matches with exact positions from source text."""
        matches: list[ContextToken] = []
        seen: set[tuple[int, int, str]] = set()

        for token in self._TOKEN_PATTERN.finditer(text):
            surface = token.group(0)
            entry = self._store.get_entry(surface)
            if entry is None:
                continue

            key = (token.start(), token.end(), entry["word"])
            if key in seen:
                continue
            seen.add(key)

            matches.append(
                ContextToken(
                    word=entry["word"],
                    start=token.start(),
                    end=token.end(),
                    meaning=self._resolve_meaning(entry, lang),
                    meaning_en=entry.get("meaning_en", ""),
                    example=entry.get("example", ""),
                    article=str(entry.get("article", "")).strip().lower(),
                )
            )

        return matches

    @staticmethod
    def _resolve_meaning(entry: dict[str, Any], lang: str) -> str:
        """Resolve meaning in requested language with Vietnamese fallback."""
        if lang == "en" and entry.get("meaning_en"):
            return entry["meaning_en"]
        return entry.get("meaning", "")
