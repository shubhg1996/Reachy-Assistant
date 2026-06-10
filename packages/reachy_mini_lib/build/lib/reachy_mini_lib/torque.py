"""Torque controller for the Reachy Mini robot."""

from .utils import wait


class TorqueController:
    """Controller for torque-related operations."""

    def __init__(self, mini):
        """Initialize the torque controller with the given mini robot."""
        self._mini = mini

    def wake_up(self):
        """Wake up the motors."""
        self._mini.enable_motors()

    def go_to_sleep(self):
        """Go to sleep."""
        self._mini.disable_motors()

    def enable_gravity_compensation(self):
        """Enable gravity compensation."""
        self._mini.enable_gravity_compensation()

    def disable_gravity_compensation(self):
        """Disable gravity compensation."""
        self._mini.disable_gravity_compensation()

    def goto_sleep_pose(self, duration=2.0):
        """Go to sleep pose."""
        self._mini.goto_sleep()
        wait(duration)
        self.go_to_sleep()
