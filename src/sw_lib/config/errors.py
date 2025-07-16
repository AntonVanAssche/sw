#!/usr/bin/env python


class ConfigError(Exception):
    """Base class for configuration-related errors."""


class ConfigLoadError(ConfigError):
    """Raised when loading the config file fails."""


class ConfigValidationError(ConfigError):
    """Raised when user config contains invalid keys or values."""


class ConfigWriteError(ConfigError):
    """Raised when saving the config file fails."""


class ConfigKeyError(ConfigError, KeyError):
    """Raised when accessing a missing or invalid config key."""
