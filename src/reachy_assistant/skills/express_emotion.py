"""OpenClaw Skill for physical animations via reachy_mini_lib."""

import random

from .base import BaseSkill


class ExpressEmotionSkill(BaseSkill):
    """Skill for triggering physical robot motion expressions based on emotion categories."""

    EMOTION_MAP = {
        "happy": ["cheerful1", "enthusiastic1", "proud1", "dance1", "welcoming1"],
        "sad": ["sad1", "downcast1", "exhausted1", "lonely1"],
        "surprised": ["surprised1", "amazed1", "oops1"],
        "fear": ["fear1", "scared1", "anxiety1"],
        "anger": ["rage1", "furious1", "frustrated1"],
        "confused": ["confused1", "uncertain1"],
        "love": ["loving1", "grateful1", "calming1"],
        "yes": ["yes1", "come1"],
        "no": ["no1", "go_away1"],
        "neutral": ["indifferent1", "helpful1", "shy1"],
    }

    def __init__(self, robot):
        """Initialize the ExpressEmotionSkill with the robot instance."""
        self.robot = robot
        self.last_emotion = None

    @property
    def name(self) -> str:
        """The exact name the LLM will use to call this tool."""
        return "express_emotion"

    @property
    def description(self) -> str:
        """Instructional text for when the LLM should invoke this tool."""
        return "Triggers physical robot motion expressions. Pass an emotion category matching the current spoken sentiment."

    def get_tool_schema(self) -> dict:
        """Return the OpenAI-compatible function definition for this tool."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "emotion": {
                            "type": "string",
                            "enum": list(self.EMOTION_MAP.keys()),
                            "description": "The emotional category mapping to Reachy's motor movements.",
                        }
                    },
                    "required": ["emotion"],
                },
            },
        }

    def execute(self, emotion: str = "neutral", **kwargs) -> str:
        """Execute the skill to trigger physical robot motion expressions."""
        print(f"[Skill] Executing emotion physical animation: {emotion}")
        category = emotion if emotion in self.EMOTION_MAP else "neutral"
        moves = self.EMOTION_MAP[category]

        if len(moves) > 1 and self.last_emotion in moves:
            moves = [m for m in moves if m != self.last_emotion]

        selected_move = random.choice(moves)
        self.last_emotion = selected_move

        try:
            self.robot.moves.play_async(selected_move)
            return f"Success. Playing physical motor animation: {selected_move}"
        except Exception as e:
            return f"Error playing animation: {e}"
