#!/usr/bin/env python3

"""
WallpaperManager module for managing wallpapers.

Includes wallpaper setting, history tracking, queue management, and config updates.
"""

import random
import subprocess
import time
from pathlib import Path

from sw.core.config import Config
from sw.core.history import HistoryIndexError, HistoryManager, HistoryWriteError
from sw.core.queue import QueueManager
from sw.utils.common import is_valid_image, replace_lines_in_file


class WallpaperError(Exception):
    """Base exception class for all wallpaper-related errors."""


class InvalidImageError(WallpaperError):
    """Raised when an invalid image file is encountered."""


class SubprocessError(WallpaperError):
    """Raised when subprocess calls (like restarting wallpaper service) fail."""


class WallpaperManager:
    """
    Core class for wallpaper management.

    Handles setting wallpapers from provided paths, queue, or random picks from directories.
    Maintains wallpaper history and updates config files accordingly.
    """

    def __init__(self):
        """Initialize with config, queue, and history managers."""
        self.config = Config()
        self.queue = QueueManager()
        self.history = HistoryManager()

    def set_wallpaper(self, path: str | Path = None) -> Path:
        """
        Set the wallpaper based on the given path or from queue/default directory.

        Resolution order:
          1. If a path is provided:
             - If it is a directory, select a random valid image inside.
             - If it is a file, use it directly.
          2. Otherwise, pop the next wallpaper from the queue if available.
          3. Otherwise, select a random wallpaper from the default wallpaper directory.

        Updates relevant config files, restarts the wallpaper daemon, and adds the wallpaper to history.

        Args:
            path (str | Path, optional): Path or directory for wallpaper. Defaults to None.

        Returns:
            Path: The path to the wallpaper that was set.

        Raises:
            InvalidImageError: If the selected file is not a valid image.
            WallpaperError: For other errors such as no valid wallpapers found.
        """
        try:
            if path:
                target = Path(path)
                if target.is_dir():
                    target = self._get_random_wallpaper(target)
            else:
                queue = self.queue.read()
                if queue:
                    target = Path(queue.pop(0))
                    self.queue.rm([str(target)])
                else:
                    target = self._get_random_wallpaper(self.config.wallpaper_dir)
        except Exception as e:
            raise WallpaperError(f"Failed to select wallpaper: {e}") from e

        if not is_valid_image(str(target)):
            raise InvalidImageError(f"Invalid image file: {target}")

        self._update_configs(str(target))
        self._restart_hyprpaper()

        try:
            self.history.add(str(target))
        except Exception as e:
            raise HistoryWriteError(f"Failed to update wallpaper history: {e}") from e

        return target

    def set_by_history_index(self, index: int) -> Path:
        """
        Set wallpaper by its index in history.

        Args:
            index (int): Zero-based index of the wallpaper in history.

        Returns:
            Path: The path to the wallpaper that was set.

        Raises:
            WallpaperError: If the index is invalid or setting wallpaper fails.
        """
        try:
            path = self.history.get_by_index(index)
        except IndexError as e:
            raise HistoryIndexError(f"Invalid history index: @{index + 1}") from e

        return self.set_wallpaper(path)

    def _get_random_wallpaper(self, directory: Path) -> Path:
        """
        Select a random valid wallpaper from a directory, excluding recent wallpapers,
        unless the directory is explicitly configured to bypass recency filtering.

        Args:
            directory (Path): Directory to pick wallpapers from.

        Returns:
            Path: Selected wallpaper path.

        Raises:
            WallpaperError: If no suitable wallpaper is found.
        """
        directory = directory.expanduser().resolve()
        recent = set(self.history.get_recent_paths())
        excludes = {Path(p).expanduser().resolve() for p in self.config.recency_exclude}
        ignore_recency = any(directory == ex or directory.is_relative_to(ex) for ex in excludes)

        candidates = []
        for f in directory.iterdir():
            if not f.is_file():
                continue

            if not is_valid_image(str(f)):
                continue

            if not ignore_recency and str(f) in recent:
                continue

            candidates.append(f)

        if not candidates:
            raise WallpaperError(f"No suitable wallpapers found in {directory}")

        return random.choice(candidates)

    def _update_configs(self, path: str):
        """
        Update configuration files for Hyprpaper and Hyprlock with the new wallpaper path.

        Args:
            path (str): The wallpaper file path to update in configs.

        Raises:
            WallpaperError: If config files cannot be updated.
        """
        try:
            replace_lines_in_file(
                self.config.hyprpaper_config_file,
                {
                    r"^(preload\s*=\s*).*$": rf"\1{path}",
                    r"^(wallpaper\s*=\s*,).*$": rf"\1{path}",
                },
            )
            replace_lines_in_file(
                self.config.hyprlock_config_file,
                {
                    r"^(\s*path\s*=\s*).*$": rf"\1{path}",
                },
            )
        except Exception as e:
            raise WallpaperError(f"Failed to update wallpaper configs: {e}") from e

    def _restart_hyprpaper(self):
        """
        Restart the Hyprpaper service to apply wallpaper changes.

        Raises:
            SubprocessError: If restarting the wallpaper daemon fails.
        """
        try:
            subprocess.run(["pkill", "-x", "hyprpaper"], check=False)
            time.sleep(1)

            # pylint: disable=consider-using-with
            subprocess.Popen(["hyprpaper"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            raise SubprocessError(f"Failed to restart hyprpaper: {e}") from e
