"""OpenClaw Skill for frame capture via iphone_cam."""

import os
from datetime import datetime

import cv2
from iphone_cam import IPhoneCamera

from .base import BaseSkill


class TakePictureSkill(BaseSkill):
    """Skill for capturing a picture using the Reachy camera."""

    def __init__(self, photos_dir="photos"):
        """Initialize the TakePictureSkill with the directory to save photos."""
        self.photos_dir = photos_dir
        os.makedirs(self.photos_dir, exist_ok=True)
        self.camera = IPhoneCamera()

    @property
    def name(self) -> str:
        """Return the function name exposed to the LLM."""
        return "take_picture"

    @property
    def description(self) -> str:
        """Return a brief description of what the tool does."""
        return "Use this tool to capture a high-definition photo using Reachy's camera."

    def get_tool_schema(self) -> dict:
        """Return the OpenAI-compatible function definition for the camera frame capture."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        }

    def execute(self, **kwargs) -> str:
        print("[Skill] Executing camera frame capture...")
        try:
            with self.camera as cam:
                frame = cam.capture_frame()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.photos_dir, f"photo_{timestamp}.jpg")
            cv2.imwrite(filepath, frame)

            # Embed a clear file token for the channels to catch
            return f"Success. Image saved to local disk. [FILE_PATH: {filepath}]"
        except Exception as e:
            return f"Error: Failed to capture picture due to hardware error: {str(e)}"
