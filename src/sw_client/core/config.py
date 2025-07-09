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
        """Initialize the Config class and load configuration data."""
        self._config_file = Path.home() / ".config" / "sw" / "config.json"

        if not self._config_file.exists():
            raise ConfigError(f"Configuration file not found at: {self._config_file}")

        try:
            with self._config_file.open("r", encoding="utf-8") as f:
                self._data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Config file is not valid JSON: {e}") from e
        except OSError as e:
            raise ConfigError(f"Could not read config file: {e}") from e

        if not isinstance(self._data, dict):
            raise ConfigError("Config file must contain a JSON object at top level.")

    def get(self, key: str, default=None):
        """Retrieve a configuration value, with optional default fallback."""
        if key not in self._data and default is None:
            raise ConfigError(f"Missing required config key: '{key}'")
        return self._data.get(key, default)

    def set(self, key: str, value) -> None:
        """Set and persist a configuration key-value pair."""
        if not self._is_valid_key(key):
            raise ConfigError(f"Invalid configuration key: '{key}' (must correspond to a property)")

        self._data[key] = value
        try:
            with self._config_file.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except OSError as e:
            raise ConfigError(f"Failed to write to config file: {e}") from e

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
    def favorites(self) -> list[Path]:
        """Return a list of favorite wallpapers."""
        favorites = self.get("favorites", [])
        if not isinstance(favorites, list):
            raise ConfigError("'favorites' must be a list")
        return [Path(f).expanduser().resolve() for f in favorites]

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
        val = self.get("history_limit", 500)
        try:
            return int(val)
        except (TypeError, ValueError) as e:
            raise ConfigError(f"Invalid value for 'history_limit' (expected int): {val}") from e

    @property
    def queue_file(self) -> Path:
        """Return the path to the queue file."""
        return Path(self.get("queue_file", "~/.cache/sw-queue")).expanduser().resolve()

    @property
    def recency_timeout(self) -> int:
        """Return the recency timeout in seconds."""
        val = self.get("recency_timeout", 3600)
        try:
            return int(val)
        except (TypeError, ValueError) as e:
            raise ConfigError(f"Invalid value for 'recency_timeout' (expected int): {val}") from e

    @property
    def recency_exclude(self) -> list[Path]:
        """Return a list of directories to exclude from recency tracking."""
        excludes = self.get("recency_exclude", [])
        if not isinstance(excludes, list):
            raise ConfigError("'recency_exclude' must be a list")
        return [Path(e).expanduser().resolve() for e in excludes]

    @property
    def wallpaper_dir(self) -> Path:
        """Return the path to the default wallpaper directory."""
        path = self.get("wallpaper_dir")
        if not path:
            raise ConfigError("Missing required config key: 'wallpaper_dir'")
        return Path(path).expanduser().resolve()
