#!/usr/bin/env python


class QueueError(Exception):
    """Base exception for queue-related errors."""


class QueueNotFoundError(QueueError):
    """Raised when the queue file is not found."""


class QueueReadError(QueueError):
    """Raised when the queue file cannot be read."""


class QueueWriteError(QueueError):
    """Raised when the queue file cannot be written to."""
