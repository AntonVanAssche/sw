#!/usr/bin/env python


class HistoryError(Exception):
    """Base exception for history-related errors."""


class HistoryNotFoundError(HistoryError):
    """Raised when the history file is not found."""


class HistoryNotReadableError(HistoryError):
    """Raised when the history file cannot be read."""


class HistoryNotWritableError(HistoryError):
    """Raised when the history file cannot be written to."""


class HistoryParseError(HistoryError):
    """Raised when there is an error parsing the history file."""


class HistoryWriteError(HistoryError):
    """Raised when there is an error writing to the history file."""


class HistoryEntryError(HistoryError):
    """Raised when there is an error with a specific history entry."""


class HistoryEntryNotFoundError(HistoryEntryError):
    """Raised when a specific history entry is not found."""
