#!/usr/bin/env python

"""
HistoryManager module for managing wallpaper history.

Includes functionality to read, write, and manipulate the history of wallpapers.
"""

import json
import time
from typing import List

from sw.core.config import Config


class HistoryEntry:
    """Represents a single entry in the wallpaper history."""

    def __init__(self, path: str, timestamp: int):
        """Initialize a history entry with a path and timestamp."""

        self.path = path
        self.time = timestamp

    def to_dict(self):
        """Convert the history entry to a dictionary format."""

        return {"path": self.path, "time": self.time}

    @staticmethod
    def from_dict(data: dict):
        """Convert a dictionary to a HistoryEntry object."""

        return HistoryEntry(path=data["path"], timestamp=data["time"])

    def __repr__(self):
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
            []: If the file is empty or unreadable.
        """

        try:
            raw = self.history_file.read_text(encoding="utf-8")
            return [HistoryEntry.from_dict(d) for d in json.loads(raw)]
        except Exception:
            return []

    def write(self, entries: List[HistoryEntry]) -> None:
        """
        Write the provided history entries to the history file.

        Args:
            entries (List[HistoryEntry]): A list of history entries to write.

        Returns:
            None: If writing is successful.

        Raises:
            RuntimeError: If writing to the file fails.
        """

        try:
            with self.history_file.open("w", encoding="utf-8") as f:
                json.dump([e.to_dict() for e in entries], f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to write history: {e}") from e

    def add(self, path: str) -> None:
        """
        Add a new entry to the history.
        If the entry already exists, it will not be added again.

        Args:
            path (str): The path of the wallpaper to add.

        Returns:
            None: If the entry is successfully added.
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

        Returns:
            None: If the entry is successfully removed.

        Raises:
            IndexError: If the index is out of range.
        """

        entries = self.read()
        if idx < 0 or idx >= len(entries):
            raise IndexError(f"Invalid history index: {idx}")

        del entries[idx]
        self.write(entries)

    def remove_all(self) -> None:
        """
        Remove all entries from the history.

        Returns:
            None: If all entries are successfully removed.
        """

        self.history_file.write_text("[]", encoding="utf-8")

    def get_recent_paths(self) -> set[str]:
        """
        Get the paths of wallpapers used within the recency timeout.

        Returns:
            set[str]: A set of paths that were used recently.
        """

        now = int(time.time())
        cutoff = now - self.recency_timeout
        return {entry.path for entry in self.read() if entry.time >= cutoff}

    def get_by_index(self, index: int) -> str:
        """
        Get the path of a wallpaper by its index in the history.

        Args:
            index (int): The index of the wallpaper in history.

        Returns:
            str: The path to the wallpaper.

        Raises:
            IndexError: If the index is out of range.
        """
        entries = self.read()
        try:
            return entries[index].path
        except IndexError as e:
            raise IndexError(f"Invalid history index: {index}") from e
