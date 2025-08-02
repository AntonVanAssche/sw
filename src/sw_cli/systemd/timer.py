#!/usr/bin/env python

import time

import dbus

from sw_cli.systemd.errors import (
    DBusConnectionError,
    SystemdError,
    SystemdTimerActionError,
    SystemdTimerNotFoundError,
    SystemdTimerStatusError,
)


class SystemdTimer:
    def __init__(self, unit_name="sw.timer"):
        self.unit_name = unit_name
        self.timer_unit = unit_name.replace(".service", ".timer")
        try:
            self.bus = dbus.SessionBus()
            self.systemd = self._get_systemd_proxy()
        except dbus.DBusException as e:
            raise DBusConnectionError() from e

    def _get_systemd_proxy(self) -> dbus.Interface:
        try:
            proxy = self.bus.get_object(
                "org.freedesktop.systemd1",
                "/org/freedesktop/systemd1",
            )
            return dbus.Interface(proxy, "org.freedesktop.systemd1.Manager")
        except dbus.DBusException as e:
            raise DBusConnectionError("Failed to connect to systemd manager.") from e

    def _get_unit_path(self) -> str:
        try:
            unit_path = self.systemd.GetUnit(self.unit_name)
            if not unit_path:
                raise SystemdTimerNotFoundError(f"Systemd unit '{self.unit_name}' not found.")
            return unit_path
        except dbus.DBusException as e:
            raise SystemdTimerNotFoundError(f"Could not find systemd unit '{self.unit_name}'.") from e

    def _get_unit_properties(self, unit_path) -> dbus.Interface:
        try:
            unit_proxy = self.bus.get_object("org.freedesktop.systemd1", unit_path)
            return dbus.Interface(unit_proxy, dbus.PROPERTIES_IFACE)
        except dbus.DBusException as e:
            raise SystemdTimerStatusError(f"Could not retrieve status for '{self.unit_name}'.") from e

    def _get_unit_file_state(self) -> str:
        try:
            return self.systemd.GetUnitFileState(self.timer_unit)
        except dbus.DBusException as e:
            raise SystemdTimerNotFoundError(f"Could not retrieve unit file state for '{self.unit_name}'.") from e

    def is_active(self) -> bool:
        try:
            unit_path = self._get_unit_path()
            properties = self._get_unit_properties(unit_path)
            return properties.Get("org.freedesktop.systemd1.Unit", "ActiveState") == "active"
        except SystemdError as e:
            raise SystemdTimerStatusError(f"Failed to determine if '{self.unit_name}' is active.") from e

    def is_enabled(self) -> bool:
        try:
            return self._get_unit_file_state() == "enabled"
        except SystemdError as e:
            raise SystemdTimerStatusError(f"Failed to determine if '{self.unit_name}' is enabled.") from e

    def enable(self) -> None:
        try:
            self.systemd.EnableUnitFiles([self.unit_name], True, False)
        except dbus.DBusException as e:
            raise SystemdTimerActionError(f"Failed to enable '{self.unit_name}'.") from e

    def disable(self) -> None:
        try:
            self.systemd.DisableUnitFiles([self.unit_name], True)
        except dbus.DBusException as e:
            raise SystemdTimerActionError(f"Failed to disable '{self.unit_name}'.") from e

    def start(self) -> None:
        try:
            self.systemd.StartUnit(self.unit_name, "replace")
        except dbus.DBusException as e:
            raise SystemdTimerActionError(f"Failed to start '{self.unit_name}'.") from e

    def stop(self) -> None:
        try:
            self.systemd.StopUnit(self.unit_name, "replace")
        except dbus.DBusException as e:
            raise SystemdTimerActionError(f"Failed to stop '{self.unit_name}'.") from e

    def toggle(self) -> None:
        try:
            if self.is_active():
                self.stop()
            else:
                self.start()
        except SystemdError as e:
            raise SystemdTimerActionError(f"Failed to toggle '{self.unit_name}'.") from e

    def next_elapse_mono(self) -> float:
        try:
            timer_path = self.systemd.LoadUnit(self.timer_unit)
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

            return remaining_usec / 1_000_000

        except dbus.DBusException as e:
            raise SystemdTimerStatusError("Unable to retrieve next elapse time.") from e

    def _get_system_uptime(self) -> float:
        return time.monotonic()
