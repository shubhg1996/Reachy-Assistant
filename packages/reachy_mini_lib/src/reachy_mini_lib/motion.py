"""Motion controller for the Reachy Mini robot."""

import numpy as np

from reachy_mini.utils import create_head_pose


class MotionController:
    """Controller for the motion of the Reachy Mini robot."""

    def __init__(self, mini):
        """Initialize the motion controller with the given Reachy Mini instance."""
        self._mini = mini

    def _goto_target(self, duration=1.0, **kwargs):
        """Move the robot to the target pose."""
        self._mini.goto_target(duration=duration, **kwargs)

    def set_head(self, roll_deg=0.0, pitch_deg=0.0, yaw_deg=0.0, duration=1.0):
        """Set the head pose of the robot."""
        target_head_pose = create_head_pose(
            roll=np.deg2rad(roll_deg),
            pitch=np.deg2rad(pitch_deg),
            yaw=np.deg2rad(yaw_deg),
            x=0.0,
            y=0.0,
            z=0.0,
            mm=False,
        )
        self._goto_target(head=target_head_pose, duration=duration)

    def set_antennas(self, right_deg=0.0, left_deg=0.0, duration=1.0):
        """Set the antennas pose of the robot."""
        antennas_rad = np.deg2rad([right_deg, left_deg])
        self._goto_target(antennas=antennas_rad, duration=duration)

    def set_body_yaw(self, yaw_deg=0.0, duration=1.0):
        """Set the body yaw of the robot."""
        self._goto_target(body_yaw=np.deg2rad(yaw_deg), duration=duration)
