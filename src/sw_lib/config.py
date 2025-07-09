#!/usr/bin/env python

import json
from pathlib import Path


class ConfigError(Exception):
    pass


class Config:
    def __init__(self, *, config_file=None, read_only=False):
        self._config_file = Path(config_file) if config_file else Path.home() / ".config" / "sw" / "config.json"
        self._read_only = read_only
        self._data = self._load_or_defaults()

    def _load_or_defaults(self):
        if not self._config_file.exists():
            return self._defaults()
        try:
            with self._config_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ConfigError("Config must be a JSON object")
                return data
        except Exception as e:
            return self._defaults()

    def _defaults(self):
        return {
            "socket_path": "/tmp/sw-daemon.sock",
            "queue_file": "~/.cache/sw-queue",
            "history_file": "~/.cache/sw-history",
            "history_limit": 500,
            "recency_timeout": 28800,
            "recency_exclude": [],
            "wallpaper_dir": str(Path.home() / "Pictures" / "Wallpapers"),
            "favorites": [],
        }

    def get(self, key, default=None):
        if key in self._data:
            return self._data[key]
        if default is not None:
            return default
        raise ConfigError(f"Missing required config key: '{key}'")

    def set(self, key, value):
        if self._read_only:
            raise ConfigError("Config is read-only, cannot set values")
        self._data[key] = value
        self._save()

    def unset(self, key):
        if self._read_only:
            raise ConfigError("Config is read-only, cannot unset values")
        if key in self._data:
            del self._data[key]
            self._save()

    def _save(self):
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            with self._config_file.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            raise ConfigError(f"Failed to write config file: {e}")

    def get_all(self):
        return dict(self._data)

    @property
    def config_file(self) -> Path:
        """Return the path to the config file."""
        return self._config_file

    @property
    def socket_path(self):
        """Return the path to the socket file."""
        return Path(self.get("socket_path", "/tmp/sw-daemon.sock")).expanduser().resolve()

    @property
    def favorites(self) -> list[Path]:
        """Return a list of favorite wallpapers."""
        favorites = self.get("favorites", [])
        if not isinstance(favorites, list):
            raise ConfigError("'favorites' must be a list")
        return [Path(f).expanduser().resolve() for f in favorites]

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
