"""OpenClaw-style Agent Runtime Engine handling multi-turn execution and native tool calling."""

import json

from llmclient import LLMClient

from ..skills.base import BaseSkill
from .memory_manager import MemoryManager


class AgentRuntime:
    """Manages the runtime execution of an OpenClaw-style agent, handling tool calling and memory management."""

    def __init__(
        self,
        llm_client: LLMClient,
        memory_manager: MemoryManager,
        model="openai/gpt-4o-mini",
    ):
        """Initialize the runtime engine with the given LLM client and memory manager."""
        self.llm = llm_client
        self.memory = memory_manager
        self.model = model

        # Dictionary to store registered skills: { "tool_name": skill_instance }
        self.skills = {}

        # In-memory short-term chat history tracking
        self.session_history = []
        self.max_session_turns = 12

        # Load the persistent state into RAM
        self.state = self.memory.load_state()

    def register_skill(self, skill: BaseSkill):
        """Inject an OpenClaw skill into the agent's runtime context."""
        self.skills[skill.name] = skill
        print(f"[Runtime] Registered skill: '{skill.name}'")

    def _compile_tools_schema(self) -> list:
        """Gather JSON schemas from all registered skills for the LLM payload."""
        return [skill.get_tool_schema() for skill in self.skills.values()]

    def run_turn(self, user_input: str) -> str:
        """Execute a single conversational cycle, handling autonomous tool calling loops."""
        print(f"\n[Runtime] Processing new user turn: '{user_input}'")

        # 1. Refresh System Prompt context from files
        system_prompt = self.memory.build_system_prompt()

        # Inject the live hardware state so the LLM is self-aware!
        live_state_context = f"\n=== CURRENT HARDWARE STATE ===\nVoice Output Enabled: {self.state.get('voice_out_enabled', False)}\n"
        system_prompt += live_state_context

        # 2. Reconstruct payload with system context + rolling session history
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.session_history)
        messages.append({"role": "user", "content": user_input})

        tools_schema = self._compile_tools_schema()

        # Execute the agentic processing loop
        while True:
            payload = {"model": self.model, "messages": messages, "temperature": 0.4}
            if tools_schema:
                payload["tools"] = tools_schema
                payload["tool_choice"] = "auto"

            print("[Runtime] Calling OpenRouter model backend...")
            # Use the underlying raw post request method to handle advanced configurations
            response_data = self.llm._post("chat/completions", payload)

            assistant_msg = response_data["choices"][0]["message"]
            messages.append(
                assistant_msg
            )  # Keep track in our execution execution trace

            # Check if the LLM wants to execute any skills
            tool_calls = assistant_msg.get("tool_calls")
            if not tool_calls:
                # No tools requested; this is the final conversational answer
                final_text = assistant_msg.get("content", "").strip()

                # Commit conversation boundaries back to long-term memory logs
                self.memory.append_interaction_memory(user_input, final_text)

                # Append to our short-term rolling memory array (RAM)
                self.session_history.append({"role": "user", "content": user_input})
                self.session_history.append(
                    {"role": "assistant", "content": final_text}
                )

                # Prune rolling chat window to prevent token explosion
                if len(self.session_history) > self.max_session_turns:
                    self.session_history = self.session_history[
                        -self.max_session_turns :
                    ]

                return final_text

            # Handle tool invocation if requested
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                tool_call_id = tool_call["id"]

                try:
                    function_args = json.loads(tool_call["function"]["arguments"])
                except Exception:
                    function_args = {}

                print(
                    f"[Runtime] LLM requested execution of tool: '{function_name}' with args: {function_args}"
                )

                if function_name in self.skills:
                    # Target and run the mapped skill
                    skill_result = self.skills[function_name].execute(**function_args)
                else:
                    skill_result = f"Error: Tool '{function_name}' is not registered on this robot configuration."

                print(f"[Runtime] Tool Execution Result: {skill_result}")

                # Append the tool execution result back into the prompt history loop
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": function_name,
                        "content": skill_result,
                    }
                )

            # Loop continues: The LLM will inspect the tool outputs and generate its final reply.
