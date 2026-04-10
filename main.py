"""
WortMeister — German Vocabulary Learning API Server
=====================================================
WortMeister – German Vocabulary Learning Backend

Core algorithms:
  • bisect   – O(log n) prefix autocomplete
  • heapq    – Min-heap SRS scheduler
  • re       – Regex translation checker
  • edge-tts – Async TTS audio generation
"""

from __future__ import annotations

import asyncio
import bisect
import hashlib
import heapq
import json
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Optional

import edge_tts
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ─── Constants ────────────────────────────────────────────────────────────────
DATA_FILE = Path(__file__).parent / "data.json"
AUDIO_CACHE_DIR = Path(tempfile.gettempdir()) / "wortmeister_audio"
AUDIO_CACHE_DIR.mkdir(exist_ok=True)
TTS_VOICE = "de-DE-ConradNeural"  # German male voice

# ─── Pydantic Models ─────────────────────────────────────────────────────────

class WordEntry(BaseModel):
    """Schema for a single vocabulary entry."""
    word: str
    meaning: str
    meaning_en: str = ""
    example: str
    translation: str
    level: str


class SearchResponse(BaseModel):
    """Response for /api/search."""
    results: list[WordEntry]


class FlashcardResponse(BaseModel):
    """Response for /api/next-card."""
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
    """Request body for /api/update-card."""
    word: str
    quality: int = Field(ge=0, le=5, description="Review quality 0-5 (SM-2 scale)")


class UpdateCardResponse(BaseModel):
    """Response for /api/update-card."""
    success: bool
    word: str
    new_interval: float
    new_due: str
    message: str


class TranslationRequest(BaseModel):
    """Request body for /api/check-translation."""
    target_word: str = Field(description="The German word the user is practising")
    user_sentence: str = Field(description="User's German sentence")


class TranslationResponse(BaseModel):
    """Response for /api/check-translation."""
    correct: bool
    target_word: str
    feedback: str


# ─── In-Memory Data Stores ───────────────────────────────────────────────────

# Loaded from data.json at startup
vocabulary: list[dict] = []           # full records
sorted_words: list[str] = []          # lowercase word list for bisect
word_index: dict[str, dict] = {}      # word (lowercase) → full record

# SRS state: list of (due_timestamp, word) managed as a min-heap
srs_heap: list[tuple[float, str]] = []
srs_cards: dict[str, dict] = {}       # word → {interval, repetitions, easiness, due}


# ─── Helper: SM-2 Algorithm ──────────────────────────────────────────────────

def sm2_update(card: dict, quality: int) -> dict:
    """
    Apply the SM-2 spaced repetition algorithm.
    quality: 0-5, where 0 = complete blackout, 5 = perfect recall.
    Returns the mutated card dict.
    """
    easiness = card["easiness"]
    repetitions = card["repetitions"]
    interval = card["interval"]

    # Update easiness factor
    easiness = max(1.3, easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    if quality < 3:
        # Failed recall → reset
        repetitions = 0
        interval = 1  # 1 day
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = interval * easiness
        repetitions += 1

    card["easiness"] = round(easiness, 2)
    card["repetitions"] = repetitions
    card["interval"] = round(interval, 2)
    card["due"] = time.time() + interval * 86400  # seconds in a day
    return card


# ─── App Initialisation ──────────────────────────────────────────────────────

app = FastAPI(
    title="WortMeister API",
    description="German vocabulary learning backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Serve Frontend ──────────────────────────────────────────────────────────

FRONTEND_DIR = Path(__file__).parent / "frontend"


@app.get("/", response_class=HTMLResponse)
def serve_root():
    """Serve the frontend SPA at root URL."""
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return index_file.read_text(encoding="utf-8")


@app.on_event("startup")
def load_data():
    """Load vocabulary from data.json and initialise SRS heap."""
    global vocabulary, sorted_words, word_index, srs_heap, srs_cards

    if not DATA_FILE.exists():
        raise RuntimeError(f"Data file not found: {DATA_FILE}")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        vocabulary = json.load(f)

    # Build sorted word list (for bisect) and index
    vocabulary.sort(key=lambda w: w["word"].lower())
    sorted_words = [entry["word"].lower() for entry in vocabulary]
    word_index = {entry["word"].lower(): entry for entry in vocabulary}

    # Initialise SRS cards — all due immediately
    now = time.time()
    for entry in vocabulary:
        w = entry["word"].lower()
        card = {
            "interval": 0,
            "repetitions": 0,
            "easiness": 2.5,
            "due": now,
        }
        srs_cards[w] = card
        heapq.heappush(srs_heap, (card["due"], w))

    print(f"✅ Loaded {len(vocabulary)} words, SRS heap size = {len(srs_heap)}")


# ─── Endpoint 1: Autocomplete Search (bisect) ────────────────────────────────

@app.get("/api/search", response_model=SearchResponse)
def search(
    q: str = Query("", min_length=0, description="Search prefix"),
    lang: str = Query("vi", description="Language for meaning: 'vi' or 'en'"),
):
    """
    Prefix-based autocomplete using bisect_left on a sorted word list.
    Time complexity: O(log n + k) where k = number of matches (capped at 10).
    Supports ?lang=vi (Vietnamese, default) or ?lang=en (English).
    """
    prefix = q.strip().lower()
    if not prefix:
        return SearchResponse(results=[])

    # Find insertion point — O(log n)
    idx = bisect.bisect_left(sorted_words, prefix)

    results: list[WordEntry] = []
    while idx < len(sorted_words) and sorted_words[idx].startswith(prefix) and len(results) < 10:
        entry = word_index[sorted_words[idx]]
        word_entry = WordEntry(**entry)
        # Swap meaning if English is requested
        if lang == "en" and entry.get("meaning_en"):
            word_entry.meaning = entry["meaning_en"]
        results.append(word_entry)
        idx += 1

    return SearchResponse(results=results)


# ─── Endpoint 2a: Get Next Flashcard (heapq) ─────────────────────────────────

@app.get("/api/next-card", response_model=FlashcardResponse)
def next_card(
    lang: str = Query("vi", description="Language for meaning: 'vi' or 'en'"),
):
    """
    Pop the most-due card from the min-heap.
    The heap is keyed by (due_timestamp, word) so the earliest-due card
    is always at the top — O(log n) pop.
    Supports ?lang=vi (Vietnamese, default) or ?lang=en (English).
    """
    if not srs_heap:
        raise HTTPException(status_code=404, detail="No cards available")

    due, word = heapq.heappop(srs_heap)
    entry = word_index.get(word)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Word '{word}' not found")

    card = srs_cards[word]
    meaning = entry["meaning"]
    if lang == "en" and entry.get("meaning_en"):
        meaning = entry["meaning_en"]

    return FlashcardResponse(
        word=entry["word"],
        meaning=meaning,
        meaning_en=entry.get("meaning_en", ""),
        example=entry["example"],
        translation=entry["translation"],
        level=entry["level"],
        interval=card["interval"],
        repetitions=card["repetitions"],
        easiness=card["easiness"],
        due=card["due"],
    )


# ─── Endpoint 2b: Update Flashcard (heapq + SM-2) ────────────────────────────

@app.post("/api/update-card", response_model=UpdateCardResponse)
def update_card(req: UpdateCardRequest):
    """
    Receive the user's self-assessed quality (0-5), run SM-2 to compute
    the next review interval, then push the card back into the heap.
    """
    word = req.word.lower()
    if word not in srs_cards:
        raise HTTPException(status_code=404, detail=f"Word '{req.word}' not in SRS")

    card = srs_cards[word]
    sm2_update(card, req.quality)

    # Push updated card back into the min-heap
    heapq.heappush(srs_heap, (card["due"], word))

    import datetime
    due_str = datetime.datetime.fromtimestamp(card["due"]).strftime("%Y-%m-%d %H:%M")

    return UpdateCardResponse(
        success=True,
        word=req.word,
        new_interval=card["interval"],
        new_due=due_str,
        message=f"Next review in {card['interval']:.1f} day(s)",
    )


# ─── Endpoint 3: Translation Check (regex) ───────────────────────────────────

@app.post("/api/check-translation", response_model=TranslationResponse)
def check_translation(req: TranslationRequest):
    """
    Check whether the user's German sentence contains the target word.
    Uses re.search with word-boundary matching and case-insensitive flag.
    Handles German umlauts (ä ö ü ß) naturally via Unicode regex.
    """
    target = req.target_word.strip()
    sentence = req.user_sentence.strip()

    if not target or not sentence:
        raise HTTPException(status_code=400, detail="Both target_word and user_sentence are required")

    # Build regex pattern: match the target word at word boundaries
    pattern = r"\b" + re.escape(target) + r"\b"
    match = re.search(pattern, sentence, re.IGNORECASE | re.UNICODE)

    if match:
        return TranslationResponse(
            correct=True,
            target_word=target,
            feedback=f"Richtig!",
        )
    else:
        return TranslationResponse(
            correct=False,
            target_word=target,
            feedback=f"Versuche es nochmal!",
        )


# ─── Endpoint 4: Text-to-Speech Audio (edge-tts) ─────────────────────────────

@app.get("/api/audio")
async def audio(word: str = Query(..., min_length=1, description="German word to pronounce")):
    """
    Generate German TTS audio using edge-tts (async).
    Audio files are cached in /tmp/wortmeister_audio/ by word hash.
    Returns audio/mpeg FileResponse.
    """
    # Deterministic cache filename
    safe_hash = hashlib.md5(word.lower().encode()).hexdigest()
    cache_path = AUDIO_CACHE_DIR / f"{safe_hash}.mp3"

    if not cache_path.exists():
        try:
            communicate = edge_tts.Communicate(word, TTS_VOICE)
            await communicate.save(str(cache_path))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")

    return FileResponse(
        path=str(cache_path),
        media_type="audio/mpeg",
        filename=f"{word}.mp3",
    )


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
