"""OpenClaw Skill allowing the agent to change its own output modalities."""

from .base import BaseSkill


class ToggleModalitySkill(BaseSkill):
    def __init__(self, runtime):
        self.runtime = runtime

    @property
    def name(self) -> str:
        return "toggle_modality"

    @property
    def description(self) -> str:
        return "Changes the output mode of the robot. Use this if the user asks you to speak out loud, or be quiet and only use text."

    def get_tool_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "enable_voice": {
                            "type": "boolean",
                            "description": "True to enable physical TTS speakers, False for text-only.",
                        }
                    },
                    "required": ["enable_voice"],
                },
            },
        }

    def execute(self, enable_voice: bool = False, **kwargs) -> str:
        """Autonomously toggles the voice output mode based on the user's request."""
        print(f"[Skill] Agent autonomously toggled voice state to: {enable_voice}")

        # 1. Update the RAM state
        self.runtime.state["voice_out_enabled"] = enable_voice

        # 2. Persist to disk so it survives reboots
        self.runtime.memory.save_state(self.runtime.state)

        mode = "VOICE and TEXT" if enable_voice else "TEXT ONLY"
        return f"Hardware state successfully updated. You are now operating in {mode} mode. Confirm this with the user."
