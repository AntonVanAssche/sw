#!/usr/bin/env python3

"""
Handles the configuration of sw.

Example config:

{
  "hyprpaper_config_file": "/path/to/hyprpaper/config/file",
  "hyprlock_config_file": "/path/to/hyprlock/config/file",
  "queue_file": "~/.cache/sw-queue",
  "history_file": "~/.cache/sw-history",
  "history_limit": 500,
  "recency_timeout": 28800,
  "recency_exclude": [
    "/path/to/dir/to/exclude1",
  ],
  "wallpaper_dir": "/path/to/default/wallpaper/dir"
}
"""

import json
from pathlib import Path


class ConfigError(Exception):
    """Custom exception for config-related errors."""


class Config:
    """Handles the configuration of sw."""

    def __init__(self):
        """Initialize the Config class."""
        self._config_file = Path.home() / ".config" / "sw" / "config.json"

        if not self._config_file.exists():
            raise ConfigError(f"Configuration file not found at {self._config_file}")

        try:
            with self._config_file.open("r", encoding="utf-8") as f:
                self._data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise ConfigError(f"Error loading config file: {e}") from e

    def get(self, key: str, default=None):
        """Retrieve a configuration value, with optional default."""
        if key not in self._data and default is None:
            raise KeyError(f"Missing required config key: '{key}'")
        return self._data.get(key, default)

    def set(self, key: str, value) -> None:
        """Set and persist a configuration key-value pair."""
        if not self._is_valid_key(key):
            raise KeyError(f"Invalid configuration key: '{key}'")

        self._data[key] = value
        try:
            with self._config_file.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except OSError as e:
            raise ConfigError(f"Error writing to config file: {e}") from e

    def get_all(self) -> dict:
        """Return the entire config as a dictionary."""
        return self._data

    def _is_valid_key(self, key: str) -> bool:
        """Only allow setting keys with a corresponding property."""
        return hasattr(self.__class__, key) and isinstance(getattr(self.__class__, key), property)

    @property
    def config_file(self) -> Path:
        """Return the path to the config file."""
        return self._config_file

    @property
    def hyprpaper_config_file(self) -> Path:
        """Return the path to the Hyprpaper configuration file."""
        return Path(self.get("hyprpaper_config_file", "~/.config/hypr/hyprpaper.conf")).expanduser().resolve()

    @property
    def hyprlock_config_file(self) -> Path:
        """Return the path to the Hyprlock configuration file."""
        return Path(self.get("hyprlock_config_file", "~/.config/hypr/hyprlock.conf")).expanduser().resolve()

    @property
    def history_file(self) -> Path:
        """Return the path to the history file."""
        return Path(self.get("history_file", "~/.cache/sw-history")).expanduser().resolve()

    @property
    def history_limit(self) -> int:
        """Return the history limit."""
        return int(self.get("history_limit", 500))

    @property
    def queue_file(self) -> Path:
        """Return the path to the queue file."""
        return Path(self.get("queue_file", "~/.cache/sw-queue")).expanduser().resolve()

    @property
    def recency_timeout(self) -> int:
        """Return the recency timeout in seconds."""
        return int(self.get("recency_timeout", 3600))

    @property
    def recency_exclude(self) -> list[Path]:
        """Return a list of directories to exclude from recency tracking."""
        return self.get("recency_exclude", [])

    @property
    def wallpaper_dir(self) -> Path:
        """Return the path to the default wallpaper directory."""
        return Path(self.get("wallpaper_dir")).expanduser().resolve()
