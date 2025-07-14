#!/usr/bin/env python

import json
from functools import cached_property
from pathlib import Path

from .errors import ConfigError, ConfigKeyError, ConfigLoadError, ConfigValidationError, ConfigWriteError


class Config:
    DEFAULT_CONFIG = {
        "wallpaper": {
            "directory": str(Path.home() / "Pictures" / "Wallpapers"),
            "favorites": [],
            "recency": {
                "exclude": [],
                "timeout": 28800,
            },
        },
        "hyprlock": {
            "config": str(Path.home() / ".config" / "hypr" / "hyprlock.conf"),
        },
        "history": {
            "file": "~/.cache/sw-history",
            "limit": 500,
        },
        "queue": {
            "file": "~/.cache/sw-queue",
        },
        "daemon": {
            "socket_path": "/tmp/sw-daemon.sock",
        },
    }

    def __init__(self, *, config_file=None, indent_json=True):
        self._config_file = Path(config_file) if config_file else Path.home() / ".config" / "sw" / "config.json"
        self._indent_json = indent_json
        self._data = self._load_merged_config()

    def _is_valid_key(self, dotted_key):
        keys = dotted_key.split(".")
        data = self.DEFAULT_CONFIG
        for key in keys:
            if not isinstance(data, dict) or key not in data:
                return False
            data = data[key]
        return True

    def _load_merged_config(self):
        """Load user config and merge with defaults."""
        config = self._deep_copy(self.DEFAULT_CONFIG)
        if self._config_file.exists():
            try:
                with self._config_file.open(encoding="utf-8") as f:
                    user_data = json.load(f)
                    if not isinstance(user_data, dict):
                        raise ConfigValidationError("Config file must contain a JSON object")
                    self._merge_dicts(config, user_data)
            except Exception as e:
                raise ConfigLoadError(f"Failed to load config: {e}") from e
        return config

    @staticmethod
    def _merge_dicts(base, override, path=""):
        for key, value in override.items():
            full_path = f"{path}.{key}" if path else key
            if key not in base:
                raise ConfigKeyError(f"Invalid config key: '{full_path}'")
            if isinstance(base[key], dict) and isinstance(value, dict):
                Config._merge_dicts(base[key], value, full_path)
            else:
                base[key] = value

    @staticmethod
    def _deep_copy(data):
        return json.loads(json.dumps(data))

    def _get_nested(self, dotted_key, default=None):
        keys = dotted_key.split(".")
        data = self._data
        for key in keys:
            if not isinstance(data, dict) or key not in data:
                if default is not None:
                    return default
                raise ConfigError(f"Invalid config key: '{dotted_key}'")
            data = data[key]
        return data

    def _set_nested(self, dotted_key, value):
        keys = dotted_key.split(".")
        data = self._data
        for key in keys[:-1]:
            if key not in data or not isinstance(data[key], dict):
                data[key] = {}
            data = data[key]
        data[keys[-1]] = value

    def _unset_nested(self, dotted_key):
        keys = dotted_key.split(".")
        data = self._data
        for key in keys[:-1]:
            if key not in data or not isinstance(data[key], dict):
                return
            data = data[key]
        data.pop(keys[-1], None)

    def _clear_cache(self):
        self.__dict__.pop("_socket_path", None)
        self.__dict__.pop("_hyprlock_config", None)
        self.__dict__.pop("_favorites", None)
        self.__dict__.pop("_history_file", None)
        self.__dict__.pop("_history_limit", None)
        self.__dict__.pop("_queue_file", None)
        self.__dict__.pop("_recency_timeout", None)
        self.__dict__.pop("_recency_exclude", None)
        self.__dict__.pop("_wallpaper_dir", None)

    def get(self, key, default=None):
        return self._get_nested(key, default)

    def set(self, key, value):
        self._set_nested(key, value)
        self._clear_cache()
        self.save()

    def unset(self, key):
        self._unset_nested(key)
        self._clear_cache()
        self.save()

    def save(self):
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            with self._config_file.open("w", encoding="utf-8") as f:
                if self._indent_json:
                    json.dump(self._data, f, indent=2)
                else:
                    json.dump(self._data, f)
        except Exception as e:
            raise ConfigWriteError(f"Failed to write config: {e}") from e

    def get_all(self):
        return self._deep_copy(self._data)

    @property
    def config_file(self) -> Path:
        return self._config_file

    @cached_property
    def socket_path(self) -> Path:
        path = self.get("daemon.socket_path")
        if not path:
            raise ConfigError("Missing required config key: 'daemon.socket_path'")
        return Path(path).expanduser().absolute()

    @cached_property
    def hyprlock_config(self) -> Path:
        path = self.get("hyprlock.config")
        if not path:
            raise ConfigError("Missing required config key: 'hyprlock.config'")
        return Path(path).expanduser().absolute()

    @cached_property
    def favorites(self) -> list[Path]:
        favs = self.get("wallpaper.favorites", [])
        if not isinstance(favs, list):
            raise ConfigError("'wallpaper.favorites' must be a list")
        return [Path(f).expanduser().absolute() for f in favs]

    @cached_property
    def history_file(self) -> Path:
        return Path(self.get("history.file")).expanduser().absolute()

    @cached_property
    def history_limit(self) -> int:
        return int(self.get("history.limit"))

    @cached_property
    def queue_file(self) -> Path:
        return Path(self.get("queue.file")).expanduser().absolute()

    @cached_property
    def recency_timeout(self) -> int:
        return int(self.get("wallpaper.recency.timeout"))

    @cached_property
    def recency_exclude(self) -> list[Path]:
        excludes = self.get("wallpaper.recency.exclude", [])
        if not isinstance(excludes, list):
            raise ConfigError("'wallpaper.recency.exclude' must be a list")
        return [Path(e).expanduser().absolute() for e in excludes]

    @cached_property
    def wallpaper_dir(self) -> Path:
        path = self.get("wallpaper.directory")
        if not path:
            raise ConfigError("Missing required config key: 'wallpaper.directory'")
        return Path(path).expanduser().absolute()
