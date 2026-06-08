"""Run the Reachy assistant: start the key listener and listen for audio input."""

from reachy_assistant import ReachyAssistant

if __name__ == "__main__":
    assistant = ReachyAssistant()
    assistant.run()
