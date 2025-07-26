#!/usr/bin/env python

from pathlib import Path

from sw_cli.ipc import SWDaemonClient, SWDaemonConnectionError, SWDaemonError, SWDaemonProtocolError
from sw_cli.utils import replace_lines_in_file
from sw_cli.wallpaper.errors import WallpaperApplyError
from sw_lib.config import Config, ConfigError, ConfigLoadError, ConfigValidationError


class WallpaperApplier:
    def __init__(self, history_manager, daemon_client=None):
        try:
            self.config = Config()

            self.hyprlock_enabled = self.config.hyprlock_enabled
            if self.hyprlock_enabled:
                if not self.config.hyprlock_config:
                    raise WallpaperApplyError("Hyprlock integration is enabled but no config file is set.")

                self.hyprlock_config = self.config.hyprlock_config
        except ConfigLoadError as e:
            raise RuntimeError("Failed to load configuration") from e
        except ConfigValidationError as e:
            raise RuntimeError("Invalid configuration") from e
        except ConfigError as e:
            raise RuntimeError("Configuration error") from e
        self.history = history_manager
        self.client = daemon_client or SWDaemonClient()

    def apply(self, path: Path):
        """
        Actually sends the set command to the daemon and updates history.
        """
        try:
            absolute_path = Path(path).resolve()
            self.client.set_wallpaper(str(absolute_path))

            if self.hyprlock_enabled:
                self._update_hyprlock_config(str(absolute_path))

            self.history.add(str(absolute_path))
        except SWDaemonConnectionError as e:
            raise WallpaperApplyError(f"Failed to connect to the daemon: {e}") from e
        except SWDaemonProtocolError as e:
            raise WallpaperApplyError(f"Protocol error while applying wallpaper: {e}") from e
        except SWDaemonError as e:
            raise WallpaperApplyError(f"Daemon error while applying wallpaper: {e}") from e
        except Exception as e:
            raise WallpaperApplyError(f"Unexpected error while applying wallpaper: {e}") from e

    def _update_hyprlock_config(self, path: str):
        try:
            replace_lines_in_file(
                self.hyprlock_config,
                {
                    r"^(\s*path\s*=\s*).*$": rf"\1{path}",
                },
            )
        except Exception as e:
            raise WallpaperApplyError(f"Failed to update wallpaper configs: {e}") from e
