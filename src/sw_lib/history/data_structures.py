#!/usr/bin/env python


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
