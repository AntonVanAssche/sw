#!/usr/bin/env python


class WallpaperError(Exception):
    """Base error for wallpaper selection problems."""


class WallpaperApplyError(WallpaperError):
    """Raised when the wallpaper fails to apply."""


class WallpaperNotFoundError(WallpaperError):
    """Raised when no suitable wallpaper is found."""
