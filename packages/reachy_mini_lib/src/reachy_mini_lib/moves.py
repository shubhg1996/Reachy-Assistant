"""MovePlayer class for playing pre-recorded moves on the Reachy Mini robot."""

import threading

from reachy_mini.motion.recorded_move import RecordedMoves


class MovePlayer:
    """A class for playing pre-recorded moves on the Reachy Mini robot.

    mini: A reference to the Reachy Mini robot.
    """

    def __init__(self, mini):
        """Initialize the MovePlayer with a reference to the Reachy Mini robot."""
        self._mini = mini

    def play_move(
        self, move_name, library_repo="pollen-robotics/reachy-mini-emotions-library"
    ):
        """Play a pre-recorded move (happy, sad, excited, etc.)."""
        moves = RecordedMoves(library_repo)
        move = moves.get(move_name)
        if move is None:
            available = moves.list_moves()
            raise ValueError(f"Move '{move_name}' not found. Available: {available}")
        self._mini.play_move(move, initial_goto_duration=1.0)

    def play_async(self, move_name):
        """Play a move asynchronously in a separate thread."""
        thread = threading.Thread(target=self.play_move, args=(move_name,))
        thread.start()
        return thread  # optional, to track completion
