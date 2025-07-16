#!/usr/bin/env python

import json
import time
from pathlib import Path
from typing import Set

from .data_structures import HistoryEntry
from .errors import (
    HistoryEntryNotFoundError,
    HistoryNotFoundError,
    HistoryNotReadableError,
    HistoryParseError,
    HistoryWriteError,
)


class HistoryManager:
    def __init__(self, history_file: Path, history_limit: int = 500, recency_timeout: int = 28800):
        self.history_file = history_file
        self.history_limit = history_limit
        self.recency_timeout = recency_timeout
        self._ensure_file()
        self.history = self._load_history()

    def _ensure_file(self) -> None:
        if not self.history_file.exists():
            try:
                self.history_file.parent.mkdir(parents=True, exist_ok=True)
                self.history_file.write_text("[]", encoding="utf-8")
            except Exception as e:
                raise HistoryWriteError(f"Failed to create history file: {e}") from e

    def _load_history(self) -> list:
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as e:
            raise HistoryNotFoundError(f"History file not found: {self.history_file}") from e
        except json.JSONDecodeError as e:
            raise HistoryParseError(f"Failed to parse history JSON: {e}") from e
        except Exception as e:
            raise HistoryNotReadableError(f"Failed to read history file: {e}") from e

    def _write(self, entries: list) -> None:
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=4)
        except Exception as e:
            raise HistoryWriteError(f"Failed to write history to file: {e}") from e

    def get(self, index: int | None = None) -> HistoryEntry | list[HistoryEntry] | None:
        try:
            if index is None:
                return [HistoryEntry.from_dict(entry) for entry in self.history]

            if -len(self.history) <= index < len(self.history):
                return HistoryEntry.from_dict(self.history[index])
        except IndexError as e:
            raise HistoryEntryNotFoundError(f"No entry found at index {index}") from e

        return None

    def add(self, path: str) -> None:
        try:
            entry = {"path": path, "time": int(time.time())}
            self.history.append(entry)
            self.history = self.history[-self.history_limit :]
            self._write(self.history)
        except HistoryWriteError as e:
            raise HistoryWriteError(f"Failed to add entry to history: {e}") from e

    def get_recent_entries(self) -> Set[HistoryEntry]:
        now = int(time.time())
        recent_entries = set()
        for entry in self.history:
            entry_time = entry["time"]
            if now - entry_time < self.recency_timeout:
                recent_entries.add(HistoryEntry.from_dict(entry))
        return recent_entries

    def is_empty(self) -> bool:
        return len(self.history) == 0

    def remove_all(self) -> None:
        try:
            self.history = []
            self._write(self.history)
        except HistoryWriteError as e:
            raise HistoryWriteError(f"Failed to clear history: {e}") from e

    def remove_by_index(self, index: int) -> None:
        try:
            del self.history[index]
            self._write(self.history)
        except IndexError as ie:
            raise HistoryEntryNotFoundError(f"No entry found at index {index}") from ie
        except HistoryWriteError as e:
            raise HistoryWriteError(f"Failed to remove entry at index {index}: {e}") from e
