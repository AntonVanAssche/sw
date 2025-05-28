#!/usr/bin/env python3

"""
TimerManager module for controlling and querying systemd timers via DBus.
"""

import time

import dbus


class TimerError(Exception):
    """Base exception class for timer-related errors."""


class DBusConnectionError(TimerError):
    """Raised when the D-Bus connection to systemd fails."""


class TimerNotFoundError(TimerError):
    """Raised when the timer unit is not found in systemd."""


class TimerStatusError(TimerError):
    """Raised when unable to determine timer status."""


class TimerUptimeReadError(TimerError):
    """Raised when the system uptime cannot be read."""


class TimerPropertyError(TimerError):
    """Raised when required properties cannot be retrieved from DBus."""


class TimerToggleError(TimerError):
    """Raised when toggling the timer state fails."""


class TimerManager:
    """Manages a user-defined systemd timer unit over DBus."""

    TIMER_UNIT = "sw.timer"

    def __init__(self):
        """Initialize DBus session and systemd manager interface."""
        try:
            self.bus = dbus.SessionBus()
            self.systemd = self._get_systemd_proxy()
        except dbus.DBusException as e:
            raise DBusConnectionError("Could not connect to D-Bus session.") from e

    def _get_systemd_proxy(self):
        """Connect to the systemd manager interface over DBus."""
        try:
            proxy = self.bus.get_object("org.freedesktop.systemd1", "/org/freedesktop/systemd1")
            return dbus.Interface(proxy, "org.freedesktop.systemd1.Manager")
        except dbus.DBusException as e:
            raise DBusConnectionError("Failed to connect to systemd manager interface.") from e

    def _get_unit(self, unit_name):
        """Fetch the object path for the given unit."""
        try:
            return self.systemd.GetUnit(unit_name)
        except dbus.DBusException as e:
            raise TimerNotFoundError(f"Systemd unit '{unit_name}' not found.") from e

    def _get_unit_properties(self, unit_path):
        """Return DBus properties interface for the unit."""
        try:
            unit_proxy = self.bus.get_object("org.freedesktop.systemd1", unit_path)
            return dbus.Interface(unit_proxy, dbus.PROPERTIES_IFACE)
        except dbus.DBusException as e:
            raise TimerPropertyError("Failed to retrieve unit properties.") from e

    def is_active(self) -> bool:
        """Return whether the timer is currently active."""
        try:
            unit_path = self._get_unit(self.TIMER_UNIT)
            props = self._get_unit_properties(unit_path)
            return props.Get("org.freedesktop.systemd1.Unit", "ActiveState") == "active"
        except dbus.DBusException as e:
            raise TimerStatusError("Could not determine if timer is active.") from e
        except TimerPropertyError as e:
            raise e

    def is_enabled(self) -> bool:
        """Check if the timer is enabled (enabled at boot)."""
        try:
            enabled_state = self.systemd.GetUnitFileState(self.TIMER_UNIT)
            return enabled_state == "enabled"
        except dbus.DBusException as e:
            raise TimerStatusError("Could not determine if timer is enabled.") from e

    def enable(self) -> str:
        """Enable and start the timer unit."""
        try:
            self.systemd.EnableUnitFiles([self.TIMER_UNIT], False, True)
            self.systemd.StartUnit(self.TIMER_UNIT, "replace")
            return "Timer enabled"
        except dbus.DBusException as e:
            raise TimerStatusError("Failed to enable or start the timer.") from e

    def disable(self) -> str:
        """Stop and disable the timer unit."""
        try:
            self.systemd.StopUnit(self.TIMER_UNIT, "replace")
            self.systemd.DisableUnitFiles([self.TIMER_UNIT], False)
            return "Timer disabled"
        except dbus.DBusException as e:
            raise TimerStatusError("Failed to stop or disable the timer.") from e

    def toggle(self) -> str:
        """Toggle the timer between enabled and disabled."""
        try:
            return self.disable() if self.is_active() else self.enable()
        except TimerError as e:
            raise TimerToggleError("Failed to toggle the timer state.") from e

    def time_left(self) -> str:
        """Return time remaining until the next trigger."""
        try:
            timer_path = self.systemd.LoadUnit(self.TIMER_UNIT)
            timer_proxy = self.bus.get_object("org.freedesktop.systemd1", timer_path)
            timer_props = dbus.Interface(timer_proxy, dbus.PROPERTIES_IFACE)

            next_elapse_mono = timer_props.Get("org.freedesktop.systemd1.Timer", "NextElapseUSecMonotonic")

            if int(next_elapse_mono) == 0:
                return "Timer is not active"

            uptime_seconds = self._get_system_uptime()
            now_usec = int(uptime_seconds * 1_000_000)
            remaining_usec = int(next_elapse_mono) - now_usec

            if remaining_usec < 0:
                return "Timer expired recently"

            return self._prettify_time(remaining_usec // 1_000_000)

        except dbus.DBusException as e:
            raise TimerStatusError("Unable to retrieve next elapse time.") from e
        except TimerUptimeReadError as e:
            raise e

    def _get_system_uptime(self) -> float:
        """Return monotonic system uptime in seconds."""
        return time.monotonic()

    def _prettify_time(self, seconds: int) -> str:
        """Convert seconds to a human-readable time string."""
        if seconds < 0:
            return "Invalid time"

        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        parts = []
        if hours:
            parts.append(f"{hours} hours")
        if minutes:
            parts.append(f"{minutes} minutes")
        if sec:
            parts.append(f"{sec} seconds")

        return ", ".join(parts) if parts else "a moment"
