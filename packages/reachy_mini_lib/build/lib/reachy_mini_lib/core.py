"""ReachyRobot: simplified wrapper for Reachy Mini SDK – works with sim and real robot."""

from reachy_mini import ReachyMini

from .audio import AudioRecorder
from .motion import MotionController
from .moves import MovePlayer
from .torque import TorqueController


class ReachyRobot:
    """Main interface to Reachy Mini.

    This class composes specialized controllers:
    - .motion  : head, antennas, body yaw
    - .torque  : wake/sleep, gravity compensation
    - .audio   : record from robot mics (with fallback)
    - .moves   : play recorded moves (e.g., emotions)
    """

    def __init__(self, media_backend="no_media"):
        """Initialize the robot.

        media_backend: "no_media" (default) disables camera/audio in the SDK.
                           Use "gstreamer" if you need media features.
        """
        if media_backend is None:
            media_backend = "no_media"
        self._media_backend = media_backend

        # Connect to the actual SDK
        self._mini = ReachyMini(media_backend=self._media_backend)

        # Compose the specialised components
        self.motion = MotionController(self._mini)
        self.torque = TorqueController(self._mini)
        self.audio = AudioRecorder()  # Does not need direct SDK access
        self.moves = MovePlayer(self._mini)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        # The SDK handles cleanup automatically; nothing special needed.
        pass

    def get_onboard_camera_frame(self):
        """Extract a raw frame matrix from Reachy Mini's native SDK camera stream."""
        # Accessing the underlying raw ReachyMini instance camera node
        if hasattr(self._mini, "camera"):
            # Fetch the latest frame from the active gstreamer stream buffer
            frame = self._mini.camera.get_frame()
            if frame is not None:
                return frame
            raise RuntimeError("SDK camera stream returned an empty frame buffer.")
        raise AttributeError(
            "The active Reachy SDK instance does not have video components initialized."
        )

    @property
    def raw(self):
        """Access the underlying ReachyMini instance for advanced use."""
        return self._mini
