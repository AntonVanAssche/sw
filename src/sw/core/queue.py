#!/usr/bin/env python3

"""
QueueManager module for controlling wallpaper queue handling.
"""

import glob
import random
from pathlib import Path

from sw.core.config import Config


class QueueError(Exception):
    """Base exception class for queue-related errors."""


class InvalidPatternError(QueueError):
    """Raised when a glob pattern is invalid or no files match."""


class QueueFileMissingError(QueueError):
    """Raised when the queue file is missing."""


class QueueFileError(QueueError):
    """Raised when there's an issue reading or writing the queue file."""


class QueueManager:
    """Manages a queue of wallpapers using glob patterns."""

    def __init__(self):
        """Initialize config and ensure queue file exists."""

        self.config = Config()
        self._ensure_queue_file()

    def _ensure_queue_file(self):
        """Make sure the queue file exists; create it if it doesn't."""

        try:
            if not self.config.queue_file.exists():
                self.config.queue_file.parent.mkdir(parents=True, exist_ok=True)
                self.config.queue_file.write_text("", encoding="utf-8")
        except Exception as e:
            raise QueueFileError(f"Error creating queue file: {e}") from e

    def read(self) -> list[Path]:
        """
        Read the queue file and return a list of wallpaper Paths.

        Raises:
            QueueFileMissingError: If queue file is missing.
            QueueFileError: For other read errors.
        """

        try:
            return [
                Path(line.strip())
                for line in self.config.queue_file.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        except FileNotFoundError as e:
            raise QueueFileMissingError("Queue file not found.") from e
        except Exception as e:
            raise QueueFileError(f"Error reading queue file: {e}") from e

    def _write(self, entries: list[Path]) -> None:
        """Write the given list of Paths to the queue file."""

        try:
            content = "\n".join(str(entry) for entry in entries)
            self.config.queue_file.write_text(content + "\n", encoding="utf-8")
        except Exception as e:
            raise QueueFileError(f"Error writing to queue file: {e}") from e

    def add(self, patterns: list[str | Path], shuffle: bool = False) -> None:
        """
        Add wallpapers to the queue from glob patterns.

        Args:
            patterns (list[str | Path]): List of glob patterns or paths.
            shuffle (bool): Whether to shuffle newly added entries before adding.

        Raises:
            InvalidPatternError: If no patterns provided or no matches found.
            QueueFileError: If writing to the queue file fails.
        """

        if not patterns:
            raise InvalidPatternError("No patterns provided for adding wallpapers.")

        new_entries: list[Path] = []

        for pattern in patterns:
            try:
                expanded = str(Path(pattern).expanduser())
                matched_files = glob.glob(expanded)

                if not matched_files:
                    raise InvalidPatternError(f"No files found for pattern: {pattern}")

                for file in matched_files:
                    path = Path(file)
                    if path not in new_entries:
                        new_entries.append(path)

            except Exception as e:
                raise InvalidPatternError(f"Error processing pattern '{pattern}': {e}") from e

        if shuffle:
            random.shuffle(new_entries)

        try:
            combined = self.read() + new_entries
            self._write(combined)
        except Exception as e:
            raise QueueFileError(f"Error updating the queue file: {e}") from e

    def rm(self, patterns: list[str | Path]) -> None:
        """
        Remove wallpapers from the queue matching given patterns.

        Args:
            patterns (list[str | Path]): List of glob patterns or paths to remove.

        Raises:
            InvalidPatternError: If no patterns provided.
            QueueFileError: If reading or writing queue file fails.
        """

        if not patterns:
            raise InvalidPatternError("No patterns provided for removal.")

        try:
            entries = self.read()
            filtered = entries

            for pattern in patterns:
                filtered = [entry for entry in filtered if not entry.match(str(pattern))]

            self._write(filtered)
        except Exception as e:
            raise QueueFileError(f"Error removing wallpapers from the queue: {e}") from e

    def list(self) -> list[Path]:
        """Return the list of all wallpapers currently in the queue."""

        return self.read()

    def empty(self) -> None:
        """Empty the entire wallpaper queue."""

        self._write([])

    def shuffle(self) -> None:
        """Shuffle the wallpapers currently in the queue."""

        try:
            entries = self.read()
            random.shuffle(entries)
            self._write(entries)
        except Exception as e:
            raise QueueFileError(f"Error shuffling the queue: {e}") from e
