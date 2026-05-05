from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse

from app.core.config import settings
from app.dependencies import get_container
from app.models.schemas import (
    ContextAnalyzeRequest,
    ContextAnalyzeResponse,
    DrillAnswerRequest,
    DrillAnswerResponse,
    DrillQuestion,
    FlashcardResponse,
    FreeTTSRequest,
    FreeTTSResponse,
    MazeMoveRequest,
    MazeMoveResponse,
    MazeSessionResponse,
    MazeStartRequest,
    NotebookDeleteResponse,
    NotebookEntryPayload,
    NotebookGroupResponse,
    NotebookListResponse,
    NotebookUpsertRequest,
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
    """Serve SPA entrypoint."""
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
    """Autocomplete vocabulary by prefix."""
    return container.search.search(q, lang)


@router.get("/api/next-card", response_model=FlashcardResponse)
def next_card(
    lang: str = Query("vi", description="Language for meaning: 'vi' or 'en'"),
    container: ServiceContainer = Depends(get_container),
) -> FlashcardResponse:
    """Return next due flashcard in SRS queue."""
    return container.srs.get_next_card(lang)


@router.post("/api/update-card", response_model=UpdateCardResponse)
def update_card(
    request: UpdateCardRequest,
    container: ServiceContainer = Depends(get_container),
) -> UpdateCardResponse:
    """Update flashcard scheduling after user self-rating."""
    return container.srs.update_card(request)


@router.post("/api/check-translation", response_model=TranslationResponse)
def check_translation(
    request: TranslationRequest,
    container: ServiceContainer = Depends(get_container),
) -> TranslationResponse:
    """Check whether target word appears in user sentence."""
    return container.translation.check_translation(request)


@router.get("/api/audio")
async def audio(
    word: str = Query(..., min_length=1, description="German word to pronounce"),
    container: ServiceContainer = Depends(get_container),
) -> FileResponse:
    """Return cached/generated TTS audio for a single word."""
    try:
        cache_path = await container.audio.get_audio_path(word)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return FileResponse(
        path=str(cache_path),
        media_type="audio/mpeg",
        filename=f"{word}.mp3",
    )


@router.get("/api/drill/next", response_model=DrillQuestion)
def drill_next(container: ServiceContainer = Depends(get_container)) -> DrillQuestion:
    """Return next noun for article/plural reflex drill."""
    return container.article_drill.get_next_question()


@router.post("/api/drill/answer", response_model=DrillAnswerResponse)
def drill_answer(
    request: DrillAnswerRequest,
    container: ServiceContainer = Depends(get_container),
) -> DrillAnswerResponse:
    """Evaluate drill answer and reschedule noun by performance."""
    return container.article_drill.submit_answer(request)


@router.post("/api/context/analyze", response_model=ContextAnalyzeResponse)
def context_analyze(
    request: ContextAnalyzeRequest,
    container: ServiceContainer = Depends(get_container),
) -> ContextAnalyzeResponse:
    """Analyze custom text and return matched vocabulary spans."""
    return container.context_analyzer.analyze(request)


@router.post("/api/audio/text", response_model=FreeTTSResponse)
async def audio_text(
    request: FreeTTSRequest,
    container: ServiceContainer = Depends(get_container),
) -> FreeTTSResponse:
    """Generate TTS for arbitrary German text and return playable URL."""
    try:
        cache_path = await container.audio.get_audio_path_for_text(request.text)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return FreeTTSResponse(
        text=request.text,
        audio_url=f"/api/audio/file/{cache_path.name}",
    )


@router.get("/api/audio/file/{filename}")
def audio_file(filename: str) -> FileResponse:
    """Serve generated TTS files by cache filename."""
    if not re.fullmatch(r"[a-f0-9]{32}\.mp3", filename):
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = settings.audio_cache_dir / filename
    if not file_path.exists() or file_path.suffix.lower() != ".mp3":
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(path=str(file_path), media_type="audio/mpeg", filename=filename)


@router.post("/api/maze/start", response_model=MazeSessionResponse)
def maze_start(
    request: MazeStartRequest,
    container: ServiceContainer = Depends(get_container),
) -> MazeSessionResponse:
    return container.maze.start_session(request)


@router.get("/api/maze/{session_id}", response_model=MazeSessionResponse)
def maze_get(
    session_id: str,
    container: ServiceContainer = Depends(get_container),
) -> MazeSessionResponse:
    return container.maze.get_session(session_id)


@router.post("/api/maze/{session_id}/move", response_model=MazeMoveResponse)
def maze_move(
    session_id: str,
    request: MazeMoveRequest,
    container: ServiceContainer = Depends(get_container),
) -> MazeMoveResponse:
    return container.maze.move(session_id, request)


@router.get("/api/notebook", response_model=NotebookListResponse)
def notebook_list(
    pos: str = Query("", description="Optional POS filter"),
    container: ServiceContainer = Depends(get_container),
) -> NotebookListResponse:
    return container.notebook.list_entries(pos)


@router.get("/api/notebook/groups", response_model=NotebookGroupResponse)
def notebook_groups(
    container: ServiceContainer = Depends(get_container),
) -> NotebookGroupResponse:
    return container.notebook.grouped_entries()


@router.post("/api/notebook", response_model=NotebookEntryPayload)
def notebook_create(
    request: NotebookUpsertRequest,
    container: ServiceContainer = Depends(get_container),
) -> NotebookEntryPayload:
    return container.notebook.upsert_entry(request)


@router.put("/api/notebook/{word}", response_model=NotebookEntryPayload)
def notebook_update(
    word: str,
    request: NotebookUpsertRequest,
    container: ServiceContainer = Depends(get_container),
) -> NotebookEntryPayload:
    if word.strip().lower() != request.word.strip().lower():
        raise HTTPException(status_code=400, detail="Path word must match payload word")
    return container.notebook.upsert_entry(request)


@router.delete("/api/notebook/{word}", response_model=NotebookDeleteResponse)
def notebook_delete(
    word: str,
    container: ServiceContainer = Depends(get_container),
) -> NotebookDeleteResponse:
    return container.notebook.delete_entry(word)
