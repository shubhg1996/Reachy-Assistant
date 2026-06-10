"""OpenClaw-style memory manager with bounded context protection to prevent file bloat."""

import json
import os
from datetime import datetime


class MemoryManager:
    def __init__(self, config_dir=None, max_recent_logs=10):
        if config_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_dir = os.path.abspath(os.path.join(current_dir, "..", "config"))
        else:
            self.config_dir = config_dir

        self.soul_path = os.path.join(self.config_dir, "SOUL.md")
        self.user_path = os.path.join(self.config_dir, "USER.md")
        self.memory_path = os.path.join(self.config_dir, "MEMORY.md")
        self.state_path = os.path.join(self.config_dir, "STATE.json")

        self.max_recent_logs = max_recent_logs
        os.makedirs(self.config_dir, exist_ok=True)
        self._init_defaults()

    def _init_defaults(self):
        defaults = {
            self.soul_path: "# Core Identity\nYou are an AI assistant managing a Reachy Mini robot.",
            self.user_path: "# User Preferences\nDirect, precise interaction.",
            self.memory_path: "# Bounded Working Memory\n\n## Long-Term Observations\n- System migrated to OpenClaw component model.\n\n## Recent Interactions\n",
        }
        for path, content in defaults.items():
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
        if not os.path.exists(self.state_path):
            with open(self.state_path, "w", encoding="utf-8") as f:
                # Default system state when booting for the very first time
                json.dump({"voice_out_enabled": False}, f, indent=4)

    def _read_file(self, file_path) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"[Memory] Error reading {os.path.basename(file_path)}: {e}")
            return ""

    def build_system_prompt(self) -> str:
        """Assembles the compiled OpenClaw context window."""
        soul = self._read_file(self.soul_path)
        user = self._read_file(self.user_path)
        working_memory = self._read_file(self.memory_path)

        return f"""
=== AGENT COGNITIVE SYSTEM PROMPT ===
{soul}

=== USER INFORMATION ===
{user}

=== PERSISTENT WORKING MEMORY ===
{working_memory}

====================================
CRITICAL OPERATIONAL RULES:
1. You have direct access to physical hardware tools (Skills). Use them whenever requested.
2. Keep spoken replies short, clean, and optimized for speech synthesis.
"""

    def append_interaction_memory(self, user_text: str, agent_text: str):
        """Maintains a strictly bounded list of recent logs inside MEMORY.md to prevent context explosion."""
        try:
            # Read current content split by lines
            with open(self.memory_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Separate static headers/long-term facts from rolling logs
            core_content = []
            recent_logs = []

            in_recent_section = False
            for line in lines:
                if "## Recent Interactions" in line:
                    in_recent_section = True
                    core_content.append(line)
                    continue

                if in_recent_section:
                    if line.strip().startswith("-"):
                        recent_logs.append(line)
                else:
                    core_content.append(line)

            # Append new event to the list
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_log = f"- [{timestamp}] User: '{user_text}' | Reachy: '{agent_text}'\n"
            recent_logs.append(new_log)

            # Slice to only keep the last N interactions
            if len(recent_logs) > self.max_recent_logs:
                recent_logs = recent_logs[-self.max_recent_logs :]

            # Rewrite the file safely
            with open(self.memory_path, "w", encoding="utf-8") as f:
                f.writelines(core_content)
                if not core_content[-1].endswith("\n"):
                    f.write("\n")
                f.writelines(recent_logs)

        except Exception as e:
            print(f"[Memory] Bounded memory optimization failed: {e}")

    def load_state(self) -> dict:
        """Load the global hardware state."""
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Memory] Failed to load state, defaulting. Error: {e}")
            return {"voice_out_enabled": False}

    def save_state(self, state_dict: dict):
        """Persist the global hardware state to disk."""
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(state_dict, f, indent=4)
        except Exception as e:
            print(f"[Memory] Failed to save state: {e}")
