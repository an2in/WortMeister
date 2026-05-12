from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from app.dsa.sort import merge_sort
from app.dsa.text_scan import is_safe_identifier


class NotebookStore:
    """Persist and query per-user notebook entries."""

    def __init__(self, state_dir: Path) -> None:
        self._state_dir = state_dir

    def list_entries(self, user_id: str) -> list[dict[str, Any]]:
        entries = self._load_entries(user_id)
        return merge_sort(list(entries.values()), key=lambda entry: str(entry.get("word", "")).lower())

    def get_entry(self, user_id: str, word: str) -> dict[str, Any] | None:
        return self._load_entries(user_id).get(word.strip().lower())

    def upsert_entry(self, user_id: str, entry: dict[str, Any]) -> dict[str, Any]:
        entries = self._load_entries(user_id)
        word = str(entry.get("word", "")).strip()
        entries[word.lower()] = entry
        self._save_entries(user_id, entries)
        return entry

    def delete_entry(self, user_id: str, word: str) -> bool:
        entries = self._load_entries(user_id)
        key = word.strip().lower()
        if key not in entries:
            return False
        del entries[key]
        self._save_entries(user_id, entries)
        return True

    def _load_entries(self, user_id: str) -> dict[str, dict[str, Any]]:
        path = self._notebook_path(user_id)
        if not path.exists():
            return {}

        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if not isinstance(payload, list):
            raise RuntimeError("Notebook dataset must be a list of entries")

        entries: dict[str, dict[str, Any]] = {}
        for item in payload:
            if not isinstance(item, dict):
                continue
            word = str(item.get("word", "")).strip()
            if word:
                entries[word.lower()] = item
        return entries

    def _save_entries(self, user_id: str, entries: dict[str, dict[str, Any]]) -> None:
        path = self._notebook_path(user_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = merge_sort(list(entries.values()), key=lambda entry: str(entry.get("word", "")).lower())
        temp_path = path.with_suffix(".tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        temp_path.replace(path)

    def _notebook_path(self, user_id: str) -> Path:
        if not is_safe_identifier(user_id):
            raise HTTPException(status_code=400, detail="Invalid user id")
        return self._state_dir / user_id / "notebook.json"
