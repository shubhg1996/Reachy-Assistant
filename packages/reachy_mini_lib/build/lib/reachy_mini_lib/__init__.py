"""Reachy Mini library: minimal wrapper around the Reachy Mini SDK with safe defaults."""

from .core import ReachyRobot
from .utils import wait

__all__ = ["ReachyRobot", "wait"]
