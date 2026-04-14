from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse

from app.core.config import settings
from app.dependencies import get_container
from app.models.schemas import (
    FlashcardResponse,
    SearchResponse,
    TranslationRequest,
    TranslationResponse,
    UpdateCardRequest,
    UpdateCardResponse,
)
from app.services.container import ServiceContainer


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def serve_root() -> str:
    index_file = settings.frontend_dir / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return index_file.read_text(encoding="utf-8")


@router.get("/api/search", response_model=SearchResponse)
def search(
    q: str = Query("", min_length=0, description="Search prefix"),
    lang: str = Query("vi", description="Language for meaning: 'vi' or 'en'"),
    container: ServiceContainer = Depends(get_container),
) -> SearchResponse:
    return container.search.search(q, lang)


@router.get("/api/next-card", response_model=FlashcardResponse)
def next_card(
    lang: str = Query("vi", description="Language for meaning: 'vi' or 'en'"),
    container: ServiceContainer = Depends(get_container),
) -> FlashcardResponse:
    return container.srs.get_next_card(lang)


@router.post("/api/update-card", response_model=UpdateCardResponse)
def update_card(
    request: UpdateCardRequest,
    container: ServiceContainer = Depends(get_container),
) -> UpdateCardResponse:
    return container.srs.update_card(request)


@router.post("/api/check-translation", response_model=TranslationResponse)
def check_translation(
    request: TranslationRequest,
    container: ServiceContainer = Depends(get_container),
) -> TranslationResponse:
    return container.translation.check_translation(request)


@router.get("/api/audio")
async def audio(
    word: str = Query(..., min_length=1, description="German word to pronounce"),
    container: ServiceContainer = Depends(get_container),
) -> FileResponse:
    try:
        cache_path = await container.audio.get_audio_path(word)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return FileResponse(
        path=str(cache_path),
        media_type="audio/mpeg",
        filename=f"{word}.mp3",
    )
