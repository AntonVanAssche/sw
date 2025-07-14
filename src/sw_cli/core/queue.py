#!/usr/bin/env python3

"""
QueueManager module for controlling wallpaper queue handling.
"""

import glob
import random
from pathlib import Path

from sw_cli.core.config import Config


class QueueError(Exception):
    """Base exception class for queue-related errors."""


class InvalidPatternError(QueueError):
    """Raised when a glob pattern is invalid or no files match."""


class QueueFileMissingError(QueueError):
    """Raised when the queue file is missing."""


class QueueFileError(QueueError):
    """Raised when there's an issue reading or writing the queue file."""


class QueueEmptyError(QueueError):
    """Raised when an operation cannot proceed because the queue is empty."""


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
            raise QueueFileError(f"Failed to initialize queue file: {e}") from e

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
            raise QueueFileMissingError("Queue file is missing.") from e
        except Exception as e:
            raise QueueFileError(f"Failed to read queue file: {e}") from e

    def _write(self, entries: list[Path]) -> None:
        """Write the given list of Paths to the queue file."""

        try:
            content = "\n".join(str(entry) for entry in entries)
            self.config.queue_file.write_text(content + ("\n" if content else ""), encoding="utf-8")
        except Exception as e:
            raise QueueFileError(f"Failed to write to queue file: {e}") from e

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
            raise InvalidPatternError("No patterns provided to add.")

        new_entries = set()

        for pattern in patterns:
            try:
                expanded = str(Path(pattern).expanduser())
                matched = glob.glob(expanded)
                if not matched:
                    raise InvalidPatternError(f"No files matched pattern: {pattern}")
                for file in matched:
                    new_entries.add(Path(file).resolve())
            except Exception as e:
                raise InvalidPatternError(f"Error processing pattern '{pattern}': {e}") from e

        if shuffle:
            new_entries = list(new_entries)
            random.shuffle(new_entries)
        else:
            new_entries = list(new_entries)

        try:
            current = self.read()
            combined = current + [p for p in new_entries if p not in current]
            self._write(combined)
            return len(new_entries)
        except Exception as e:
            raise QueueFileError(f"Failed to update queue with new entries: {e}") from e

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
            before = len(entries)

            def match_any(entry: Path) -> bool:
                return any(entry.match(str(p)) for p in patterns)

            filtered = [e for e in entries if not match_any(e)]
            removed = before - len(filtered)

            self._write(filtered)

            return removed
        except Exception as e:
            raise QueueFileError(f"Failed to remove entries from queue: {e}") from e

    def list(self) -> list[Path]:
        """Return the list of all wallpapers currently in the queue."""

        try:
            entries = self.read()
            if not entries:
                raise QueueEmptyError("The queue is empty.")

            return entries
        except QueueFileMissingError as e:
            raise e
        except QueueEmptyError as e:
            raise e
        except Exception as e:
            raise QueueFileError(f"Failed to read queue entries: {e}") from e

    def empty(self) -> None:
        """Empty the entire wallpaper queue."""

        self._write([])

    def shuffle(self) -> None:
        """Shuffle the wallpapers currently in the queue."""

        try:
            entries = self.read()
            if not entries:
                raise QueueEmptyError("Cannot shuffle an empty queue.")

            random.shuffle(entries)
            self._write(entries)
        except QueueEmptyError as e:
            raise e
        except Exception as e:
            raise QueueFileError(f"Failed to shuffle queue: {e}") from e
