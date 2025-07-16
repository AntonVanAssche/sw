#!/usr/bin/env python

import random
import time
from pathlib import Path

from sw_cli.utils.common import is_valid_image
from sw_cli.wallpaper.errors import WallpaperError, WallpaperNotFoundError


class WallpaperDirectoryError(WallpaperError):
    """Raised when there is an issue accessing a wallpaper directory."""


class WallpaperSelector:
    def __init__(self, config, queue_manager, history_manager):
        self.config = config
        self.queue = queue_manager
        self.history = history_manager

    def select_wallpaper(self, path: str | Path = None, use_dir: bool = False) -> Path:
        """
        Figure out what wallpaper path to set.

        If use_dir is True, pick from the directory of the current wallpaper.
        """
        try:
            if use_dir:
                current_wallpaper = self.history.get(-1)
                if current_wallpaper:
                    current_dir = Path(current_wallpaper).parent
                    return self._pick_from_directory(current_dir)

                raise WallpaperNotFoundError("No current wallpaper found in history to determine directory.")

            if path:
                target = Path(path)
                if not target.exists():
                    raise WallpaperNotFoundError(f"Specified path does not exist: {target}")
                if target.is_dir():
                    return self._pick_from_directory(target)
                if not is_valid_image(str(target)):
                    raise WallpaperError(f"Specified file is not a valid image: {target}")
                return target

            queued = self.queue.get()
            if queued:
                next_item = Path(queued.pop(0))
                self.queue.remove([str(next_item)])
                if not next_item.exists():
                    raise WallpaperNotFoundError(f"Queued wallpaper does not exist: {next_item}")
                if not is_valid_image(str(next_item)):
                    raise WallpaperError(f"Queued wallpaper is not a valid image: {next_item}")
                return next_item

            # Finally fallback to config wallpaper dir
            return self._pick_from_directory(self.config.wallpaper_dir)

        except (WallpaperNotFoundError, WallpaperError):
            raise  # re-raise known errors unchanged
        except Exception as e:
            raise WallpaperError(f"Unexpected error selecting wallpaper: {e}") from e

    def _pick_from_directory(self, directory: Path) -> Path:
        """
        Pick a random image in a dir, respecting recency rules.
        """
        try:
            directory = directory.expanduser().resolve()
            if not directory.exists() or not directory.is_dir():
                raise WallpaperDirectoryError(f"Invalid wallpaper directory: {directory}")

            now = time.time()
            exclude_dirs = {Path(p).expanduser().resolve() for p in self.config.recency_exclude}

            recent_entries = self.history.get_recent_entries()
            recent_paths = set()

            for entry in recent_entries:
                entry_path = Path(entry.path).expanduser().resolve()
                entry_dir = entry_path.parent

                if self.config.recency_timeout and (now - entry.time) < self.config.recency_timeout:
                    if not any(entry_dir == ex or entry_dir.is_relative_to(ex) for ex in exclude_dirs):
                        recent_paths.add(str(entry_path))

            candidates = [
                f for f in directory.iterdir() if f.is_file() and is_valid_image(str(f)) and str(f) not in recent_paths
            ]

            if not candidates:
                raise WallpaperNotFoundError(f"No suitable wallpapers found in {directory}")

            return random.choice(candidates)

        except WallpaperError:
            raise
        except Exception as e:
            raise WallpaperError(f"Error picking wallpaper from directory {directory}: {e}") from e
