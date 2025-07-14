#!/usr/bin/env python


class SystemdError(Exception):
    """Base class for all systemd-related exceptions."""


class DBusConnectionError(SystemdError):
    """Raised when there is an issue connecting to the D-Bus session."""

    def __init__(self, message="Could not connect to D-Bus session."):
        super().__init__(message)


class SystemdTimerNotFoundError(SystemdError):
    """Raised when the systemd timer unit is not found."""

    def __init__(self, message="Systemd timer unit not found."):
        super().__init__(message)


class SystemdTimerStatusError(SystemdError):
    """Raised when there is an issue retrieving the status of the systemd timer."""

    def __init__(self, message="Could not retrieve the status of the systemd timer."):
        super().__init__(message)


class SystemdTimerActionError(SystemdError):
    """Raised when there is an issue performing an action on the systemd timer."""

    def __init__(self, message="Could not perform the action on the systemd timer."):
        super().__init__(message)
