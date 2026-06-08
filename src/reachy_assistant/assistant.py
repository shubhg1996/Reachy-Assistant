"""Reachy Assistant: a voice-controlled robot assistant using STT, LLM, and TTS."""

import tempfile
import threading

import soundfile as sf
from llmclient import LLMClient
from reachy_mini_lib import ReachyRobot
from speech2text import Speech2Text
from ttsclient import TextToSpeech

from .action_mapper import ActionMapper
from .key_listener import KeyListener


class ReachyAssistant:
    """Manages the voice assistant workflow: STT, LLM, TTS, and robot actions."""

    def __init__(
        self,
        llm_model="openai/gpt-3.5-turbo",
        stt_model="base",
        tts_voice="en-US-JennyNeural",
    ):
        """Initialize the assistant with the specified models and voice."""
        self.stt = Speech2Text(model_name=stt_model)
        print(f"STT model '{stt_model}' loaded.")
        self.llm = LLMClient()
        print("LLM client initialized.")
        self.tts = TextToSpeech(voice=tts_voice)
        print(f"TTS voice '{tts_voice}' loaded.")
        self.robot = ReachyRobot()
        print("Reachy robot initialized.")
        self.action = ActionMapper(self.robot)
        print("Action mapper initialized.")
        self.key_listener = KeyListener(self._on_audio_ready)
        print("Key listener initialized.")

    def run(self):
        """Run the assistant: start the key listener and listen for audio input."""
        print("Hold SPACE to speak to Reachy. Release to get a response.")
        with self.robot:
            self.robot.torque.wake_up()
            self.key_listener.start()  # blocks

    def _on_audio_ready(self, audio_np):
        # 1. Save temporary WAV
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sf.write(tmp.name, audio_np, 16000)
            tmp_path = tmp.name

        # 2. STT
        text = self.stt.transcribe(tmp_path)
        print(f"User said: {text}")
        if not text.strip():
            return

        # 3. LLM
        response = self.llm.generate(text)
        print(f"Reachy says: {response}")

        # 4. TTS -> audio file
        tts_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        self.tts.save(response, tts_file)

        # 5. Play audio on robot speakers (fallback to local)
        audio_thread = threading.Thread(
            target=self.robot.audio.play_async, args=(tts_file,)
        )
        motion_thread = threading.Thread(target=self.action.execute, args=(response,))
        audio_thread.start()
        motion_thread.start()

        audio_thread.join()
        motion_thread.join()
