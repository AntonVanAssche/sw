#!/usr/bin/env python

"""
HistoryManager module for managing wallpaper history.

Includes functionality to read, write, and manipulate the history of wallpapers.
"""

import json
import time
from typing import List, Set

from sw_cli.core.config import Config


class HistoryError(Exception):
    """Base exception for history-related errors."""


class HistoryReadError(HistoryError):
    """Exception raised when reading history fails."""


class HistoryWriteError(HistoryError):
    """Exception raised when writing history fails."""


class HistoryIndexError(HistoryError, IndexError):
    """Exception raised for invalid history index access."""


class HistoryEntry:
    """Represents a single entry in the wallpaper history."""

    def __init__(self, path: str, timestamp: int):
        """Initialize a history entry with a path and timestamp."""
        self.path = path
        self.time = timestamp

    def to_dict(self) -> dict:
        """Convert the history entry to a dictionary format."""
        return {"path": self.path, "time": self.time}

    @staticmethod
    def from_dict(data: dict) -> "HistoryEntry":
        """Convert a dictionary to a HistoryEntry object."""
        return HistoryEntry(path=data["path"], timestamp=data["time"])

    def __repr__(self) -> str:
        """String representation of the HistoryEntry object."""
        return f"<HistoryEntry path={self.path} time={self.time}>"


class HistoryManager:
    """
    Core class for managing wallpaper history.

    Handles reading, writing, and manipulating the history of wallpapers.
    """

    def __init__(self):
        """Initialize the HistoryManager with a history file."""
        self.config = Config()
        self.history_file = self.config.history_file
        self.history_limit = self.config.history_limit
        self.recency_timeout = self.config.recency_timeout
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Ensure the history file exists; create it if it doesn't."""
        if not self.history_file.exists():
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self.history_file.write_text("[]", encoding="utf-8")

    def read(self) -> List[HistoryEntry]:
        """
        Read the history file and return a list of HistoryEntry objects.

        Returns:
            List[HistoryEntry]: A list of history entries.

        Raises:
            HistoryReadError: If reading or parsing the history file fails.
        """
        try:
            raw = self.history_file.read_text(encoding="utf-8")
            data = json.loads(raw)
            if not isinstance(data, list):
                raise HistoryReadError("History data is not a list")
            return [HistoryEntry.from_dict(d) for d in data]
        except (json.JSONDecodeError, OSError) as e:
            raise HistoryReadError(f"Failed to read history file: {e}") from e
        except Exception as e:
            raise HistoryReadError(f"Unexpected error reading history: {e}") from e

    def write(self, entries: List[HistoryEntry]) -> None:
        """
        Write the provided history entries to the history file.

        Args:
            entries (List[HistoryEntry]): A list of history entries to write.

        Raises:
            HistoryWriteError: If writing to the file fails.
        """
        try:
            with self.history_file.open("w", encoding="utf-8") as f:
                json.dump([e.to_dict() for e in entries], f, indent=2)
        except OSError as e:
            raise HistoryWriteError(f"Failed to write history: {e}") from e
        except Exception as e:
            raise HistoryWriteError(f"Unexpected error writing history: {e}") from e

    def add(self, path: str) -> None:
        """
        Add a new entry to the history.
        If the entry already exists as the last one, it will not be added again.

        Args:
            path (str): The path of the wallpaper to add.

        Raises:
            HistoryReadError: If reading history fails.
            HistoryWriteError: If writing history fails.
        """
        now = int(time.time())
        entries = self.read()

        if not entries or entries[-1].path != path:
            entries.append(HistoryEntry(path, now))
            entries = entries[-self.history_limit :]

        self.write(entries)

    def remove_by_index(self, idx: int) -> None:
        """
        Remove an entry from the history by its index.

        Args:
            idx (int): The index of the entry to remove.

        Raises:
            HistoryReadError: If reading history fails.
            HistoryWriteError: If writing history fails.
            HistoryIndexError: If the index is out of range.
        """
        entries = self.read()
        if idx < 0 or idx >= len(entries):
            raise HistoryIndexError(f"Invalid history index: {idx}")

        del entries[idx]
        self.write(entries)

    def remove_all(self) -> None:
        """
        Remove all entries from the history.

        Raises:
            HistoryWriteError: If clearing the history file fails.
        """
        try:
            self.history_file.write_text("[]", encoding="utf-8")
        except OSError as e:
            raise HistoryWriteError(f"Failed to clear history file: {e}") from e

    def get_recent_paths(self) -> Set[str]:
        """
        Get the paths of wallpapers used within the recency timeout.

        Returns:
            Set[str]: A set of paths that were used recently.

        Raises:
            HistoryReadError: If reading history fails.
        """
        now = int(time.time())
        cutoff = now - self.recency_timeout
        entries = self.read()
        return {entry.path for entry in entries if entry.time >= cutoff}

    def get_by_index(self, index: int) -> str:
        """
        Get the path of a wallpaper by its index in the history.

        Args:
            index (int): The index of the wallpaper in history.

        Returns:
            str: The path to the wallpaper.

        Raises:
            HistoryReadError: If reading history fails.
            HistoryIndexError: If the index is out of range.
        """
        entries = self.read()
        try:
            return entries[index].path
        except IndexError as e:
            raise HistoryIndexError(f"Invalid history index: {index}") from e
