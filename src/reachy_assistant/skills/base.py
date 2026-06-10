"""Base contract for OpenClaw-style skills."""

from abc import ABC, abstractmethod


class BaseSkill(ABC):
    """Abstract base class for all OpenClaw-style skills."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The function name exposed to the LLM."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Instructional text for when the LLM should invoke this tool."""
        pass

    @abstractmethod
    def get_tool_schema(self) -> dict:
        """Return the OpenAI-compatible function definition."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool and returns text results to the agent loop."""
        pass
