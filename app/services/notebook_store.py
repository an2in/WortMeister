from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class NotebookStore:
    """Persist and query user-created notebook entries."""

    def __init__(self, data_file: Path) -> None:
        self._data_file = data_file
        self._entries: dict[str, dict[str, Any]] = {}

    def load(self) -> None:
        if not self._data_file.exists():
            self._entries = {}
            self.save()
            return

        with self._data_file.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if not isinstance(payload, list):
            raise RuntimeError("Notebook dataset must be a list of entries")

        self._entries = {}
        for item in payload:
            if not isinstance(item, dict):
                continue
            word = str(item.get("word", "")).strip()
            if not word:
                continue
            self._entries[word.lower()] = item

    def save(self) -> None:
        self._data_file.write_text(
            json.dumps(self.list_entries(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def list_entries(self) -> list[dict[str, Any]]:
        return sorted(self._entries.values(), key=lambda entry: str(entry.get("word", "")).lower())

    def get_entry(self, word: str) -> dict[str, Any] | None:
        return self._entries.get(word.strip().lower())

    def upsert_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        word = str(entry.get("word", "")).strip()
        self._entries[word.lower()] = entry
        self.save()
        return entry

    def delete_entry(self, word: str) -> bool:
        key = word.strip().lower()
        if key not in self._entries:
            return False
        del self._entries[key]
        self.save()
        return True
