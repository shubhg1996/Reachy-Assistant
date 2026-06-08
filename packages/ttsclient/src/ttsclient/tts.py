"""Text-to-Speech client using edge_tts"""

import asyncio

import edge_tts


class TextToSpeech:
    """Text-to-Speech client using edge_tts."""

    def __init__(self, voice="en-US-JennyNeural"):
        """Initialize with the desired voice."""
        self.voice = voice

    def save(self, text, output_file="output.mp3"):
        """Convert text to speech and save to file."""

        async def _save():
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_file)

        asyncio.run(_save())
        return output_file

    def speak(self, text):
        """Directly play audio (requires pygame or system player)."""
        # Minimal: just save and optionally play using default player
        output = self.save(text, "temp_speech.mp3")
        import platform
        import subprocess

        if platform.system() == "Darwin":  # macOS
            subprocess.run(["afplay", output])
        elif platform.system() == "Windows":
            subprocess.run(["start", output], shell=True)
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", output])
