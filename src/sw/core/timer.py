#!/usr/bin/env python3

"""
TimerManager module for controlling and querying systemd timers via DBus.
"""

import dbus


class TimerError(Exception):
    """Base exception class for timer-related errors."""


class TimerManager:
    """Manages a user-defined systemd timer unit over DBus."""

    TIMER_UNIT = "sw.timer"

    def __init__(self):
        """Initialize DBus session and systemd manager interface."""

        self.bus = dbus.SessionBus()
        self.systemd = self._get_systemd_proxy()

    def _get_systemd_proxy(self):
        """Connect to the systemd manager interface over DBus."""

        try:
            proxy = self.bus.get_object("org.freedesktop.systemd1", "/org/freedesktop/systemd1")
            return dbus.Interface(proxy, "org.freedesktop.systemd1.Manager")
        except dbus.DBusException as e:
            raise TimerError("Failed to connect to systemd over D-Bus") from e

    def _get_unit(self, unit_name):
        """Fetch the object path for the given unit."""

        try:
            return self.systemd.GetUnit(unit_name)
        except dbus.DBusException as e:
            raise TimerError(f"Failed to get unit '{unit_name}'") from e

    def _get_unit_properties(self, unit_path):
        """Return DBus properties interface for the unit."""

        unit_proxy = self.bus.get_object("org.freedesktop.systemd1", unit_path)
        return dbus.Interface(unit_proxy, dbus.PROPERTIES_IFACE)

    def is_active(self) -> bool:
        """
        Check whether the timer unit is active.

        Returns:
            bool: True if the timer is active, False otherwise.

        Raises:
            TimerError: If there is a failure in checking the timer's active state.
        """

        try:
            unit_path = self._get_unit(self.TIMER_UNIT)
            props = self._get_unit_properties(unit_path)
            return props.Get("org.freedesktop.systemd1.Unit", "ActiveState") == "active"
        except dbus.DBusException as e:
            raise TimerError("Failed to check active state") from e

    def is_enabled(self) -> bool:
        """
        Check if the timer unit is enabled (will start on boot).

        Returns:
            bool: True if the timer is enabled, False otherwise.

        Raises:
            TimerError: If there is a failure in checking the timer's enabled state.
        """

        try:
            enabled_state = self.systemd.GetUnitFileState(self.TIMER_UNIT)
            return enabled_state == "enabled"
        except dbus.DBusException as e:
            raise TimerError("Failed to get enabled state") from e

    def enable(self) -> str:
        """
        Enable and start the timer unit.

        Returns:
            str: Success message indicating the timer is enabled.

        Raises:
            TimerError: If there is a failure in enabling or starting the timer.
        """

        try:
            self.systemd.EnableUnitFiles([self.TIMER_UNIT], False, True)
            self.systemd.StartUnit(self.TIMER_UNIT, "replace")
            return "Timer enabled"
        except dbus.DBusException as e:
            raise TimerError("Failed to enable/start timer") from e

    def disable(self) -> str:
        """
        Stop and disable the timer unit.

        Returns:
            str: Success message indicating the timer is disabled.

        Raises:
            TimerError: If there is a failure in stopping or disabling the timer.
        """

        try:
            self.systemd.StopUnit(self.TIMER_UNIT, "replace")
            self.systemd.DisableUnitFiles([self.TIMER_UNIT], False)
            return "Timer disabled"
        except dbus.DBusException as e:
            raise TimerError("Failed to stop/disable timer") from e

    def toggle(self) -> str:
        """
        Toggle the timer between enabled/disabled.

        Returns:
            str: Success message indicating the timer's new state.

        Raises:
            TimerError: If there is a failure in toggling the timer.
        """

        try:
            return self.disable() if self.is_active() else self.enable()
        except TimerError as e:
            raise TimerError("Failed to toggle timer") from e

    def time_left(self) -> str:
        """
        Calculate and return remaining time until the timer triggers.

        Returns:
            str: A human-readable string indicating the time left until the next trigger.

        Raises:
            TimerError: If there is a failure in retrieving timer information.
        """
        try:
            timer_path = self.systemd.LoadUnit(self.TIMER_UNIT)
            timer_proxy = self.bus.get_object("org.freedesktop.systemd1", timer_path)
            timer_props = dbus.Interface(timer_proxy, dbus.PROPERTIES_IFACE)

            next_elapse_mono = timer_props.Get("org.freedesktop.systemd1.Timer", "NextElapseUSecMonotonic")

            if int(next_elapse_mono) == 0:
                return "Timer is not active"

            # Get current monotonic time in microseconds.
            try:
                with open("/proc/uptime", "r", encoding="utf-8") as f:
                    uptime_seconds = float(f.readline().split()[0])
            except OSError as e:
                raise TimerError("Failed to read system uptime") from e

            now_usec = int(uptime_seconds * 1_000_000)
            remaining_usec = int(next_elapse_mono) - now_usec

            if remaining_usec < 0:
                return "Timer expired recently"

            return self._prettify_time(remaining_usec // 1_000_000)

        except dbus.DBusException as e:
            raise TimerError("Failed to get monotonic timer info") from e

    def _prettify_time(self, seconds: int) -> str:
        """
        Convert raw seconds into a human-friendly duration string.

        Returns:
            str: A string representing the time in hours, minutes, and seconds.
        """

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
