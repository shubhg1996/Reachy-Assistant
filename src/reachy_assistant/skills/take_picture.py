"""OpenClaw Skill allowing the agent to pick between native robot vision or external system optics."""

import os
from datetime import datetime

import cv2
import numpy as np
from iphone_cam import IPhoneCamera

from .base import BaseSkill


class TakePictureSkill(BaseSkill):
    def __init__(self, robot, photos_dir="photos"):
        self.robot = robot
        self.photos_dir = photos_dir
        os.makedirs(self.photos_dir, exist_ok=True)
        self.external_camera = IPhoneCamera()

    @property
    def name(self) -> str:
        return "take_picture"

    @property
    def description(self) -> str:
        return (
            "Captures a photo from the robot's physical eyes ('reachy_mini_head') or external optics ('host_system'). "
            "Use this tool ANYTIME the user asks you a question that requires vision, such as describing what is in front of you, "
            "identifying an object on the table, evaluating a gesture, or reading text held up to your face. "
            "Executing this tool will automatically stream the captured frame directly into your cognitive input buffer."
        )

    def get_tool_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "enum": ["host_system", "reachy_mini_head"],
                            "description": "The target camera hardware vector to execute the capture frame sequence on.",
                        }
                    },
                    "required": ["source"],
                },
            },
        }

    def execute(self, source: str = "host_system", **kwargs) -> str:
        print(
            f"[Skill: Camera] Initiating frame execution sequence via source context: '{source}'"
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # DYNAMIC SIMULATION OVERRIDE CHECK
            # If the LLM requests the robot's head camera, but we detect the SDK is running
            # in simulation/mock mode, automatically swap the source vector to the laptop camera.
            if source == "reachy_mini_head":
                is_sim = False

                # Check standard Pollen SDK signatures for active simulation profiles
                if hasattr(self.robot._mini, "is_sim") and self.robot._mini.is_sim:
                    is_sim = True
                elif (
                    hasattr(self.robot._mini, "backend_type")
                    and "mujoco" in str(self.robot._mini.backend_type).lower()
                ):
                    is_sim = True

                if is_sim:
                    print(
                        "[Skill: Camera] Simulation mode detected! Overriding 'reachy_mini_head' to utilize laptop vision."
                    )
                    source = "host_system"  # Cleanly swap the routing pointer

            # --- EXECUTION PATHS ---
            if source == "reachy_mini_head":
                # Real physical hardware path
                filepath = os.path.join(
                    self.photos_dir, f"photo_reachy_head_{timestamp}.jpg"
                )
                raw_frame = self.robot._mini.media.get_frame()
                if raw_frame is None or raw_frame.size == 0:
                    raise RuntimeError(
                        "Reachy Mini SDK camera stream returned an empty frame array buffer."
                    )

                frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)

                # Programmatic Exposure Compensation for the dark lens issue
                lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                l_channel, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                cl = clahe.apply(l_channel)
                limg = cv2.merge((cl, a, b))
                enhanced_frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
                enhanced_frame = cv2.convertScaleAbs(enhanced_frame, alpha=1.3, beta=25)

                cv2.imwrite(filepath, enhanced_frame)
                return f"Success. Captured first-person robot viewpoint. [FILE_PATH: {filepath}]"

            else:
                # Host system (Laptop / iPhone Continuity) path
                filepath = os.path.join(
                    self.photos_dir, f"photo_host_system_{timestamp}.jpg"
                )
                with self.external_camera as cam:
                    frame = cam.capture_frame()
                cv2.imwrite(filepath, frame)

                # Adjust the return string based on why we used the laptop camera
                message = "Photo captured via main system."
                if kwargs.get("sim_overridden", False) or source == "host_system":
                    # If it was redirected because of sim, let the LLM know so it can tailor its response text
                    if source == "host_system" and "is_sim" in locals() and is_sim:
                        message = "Captured environmental frame via host laptop camera (Robot is operating in a virtual simulator environment)."

                return f"Success. {message} [FILE_PATH: {filepath}]"

        except Exception as e:
            return (
                f"Error: Failed to process camera turn for source '{source}': {str(e)}"
            )
