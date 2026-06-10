import tempfile
import threading
import time

import numpy as np
import sounddevice as sd
import soundfile as sf
from llmclient import LLMClient
from reachy_mini_lib import ReachyRobot
from speech2text import Speech2Text
from ttsclient import TextToSpeech
from wakeword import WakeWordDetector

from .action_mapper import ActionMapper
from .camera_handler import CameraHandler
from .intent_handlers import IntentHandlers


class ReachyAssistant:
    def __init__(
        self,
        llm_model="openai/gpt-3.5-turbo",
        stt_model="base",
        tts_voice="en-US-JennyNeural",
    ):
        self.stt = Speech2Text(model_name=stt_model)
        self.llm = LLMClient()
        self.tts = TextToSpeech(voice=tts_voice)
        self.robot = ReachyRobot()
        self.action = ActionMapper(self.robot)
        self.camera = CameraHandler()
        self.intent_handlers = IntentHandlers(self.camera)

        # Wake word detector
        self.wake_detector = WakeWordDetector(
            wakeword="hey_mycroft", vad_threshold=0.35, sensitivity=0.5
        )
        self.wake_detector.on_wake_word(self._on_wake_word_signal)

        # Event to signal main thread that a wake word was detected
        self.command_event = threading.Event()
        self.command_pending = False
        self.ignore_wake = False

    def run(self):
        print("Wake word: 'hey mycroft'. Say it to start speaking.")
        with self.robot:
            self.robot.torque.wake_up()
            self.wake_detector.start()
            try:
                while True:
                    # Wait for the wake word signal
                    self.command_event.wait()
                    self.command_event.clear()
                    self.command_pending = False
                    # Process the entire command flow in the main thread
                    self._process_command_flow()
            except KeyboardInterrupt:
                self.wake_detector.stop()
                print("Stopped.")

    def _on_wake_word_signal(self):
        """Called from wake word detector thread – only signal if not ignored."""
        if not self.ignore_wake and not self.command_pending:
            self.command_pending = True
            self.command_event.set()

    def _process_command_flow(self):
        print("🔊 Wake word detected! Recording command...")
        # Disable wake callbacks while processing
        self.ignore_wake = True

        audio_np = self._record_audio(duration=4.0, samplerate=16000)
        if audio_np is not None:
            rms = np.sqrt(np.mean(audio_np.astype(np.float32) ** 2))
            if rms > 0.01:
                self._on_audio_ready(audio_np)

        # Wait a little for residual sound to fade
        time.sleep(0.5)
        # Re‑enable wake callbacks
        self.ignore_wake = False

    def _record_audio(self, duration=4.0, samplerate=16000):
        """Record audio for a fixed duration using a queue-based callback."""
        import queue

        audio_queue = queue.Queue()
        recording = []

        def callback(indata, frames, time, status):
            if status:
                print(f"Audio callback status: {status}")
            audio_queue.put(indata.copy())

        try:
            stream = sd.InputStream(
                samplerate=samplerate, channels=1, dtype="float32", callback=callback
            )
            stream.start()
            print(f"Recording for {duration} seconds...")

            remaining = duration
            while remaining > 0:
                try:
                    data = audio_queue.get(timeout=0.1)
                    recording.append(data)
                    remaining -= data.shape[0] / samplerate
                except queue.Empty:
                    continue

            stream.stop()
            stream.close()

            audio_np = np.concatenate(recording, axis=0).flatten()
            audio_int16 = (audio_np * 32767).astype(np.int16)
            print("Recording finished.")
            return audio_int16

        except Exception as e:
            print(f"Recording error: {e}")
            if "stream" in locals():
                stream.stop()
                stream.close()
            return None

    def _on_audio_ready(self, audio_np):
        """Transcribe, call LLM, generate TTS, and animate robot."""
        # Save temporary WAV
        print("Saving temporary WAV...")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sf.write(tmp.name, audio_np, 16000)
            tmp_path = tmp.name

        # STT
        print("Transcribing...")
        text = self.stt.transcribe(tmp_path)
        if not text.strip():
            print("Empty transcription, ignoring.")
            return
        print(f"STT: {text}")

        # LLM with intent detection
        intent, response, params = self.llm.generate_with_intent(
            text, intents=["take_picture", "chat"]
        )
        print(f"LLM raw response: {response}")

        # Execute intent handler (may modify response)
        final_response = self.intent_handlers.process(intent, response, params)
        print(f"Intent: {intent}, Final response: {final_response}")

        # TTS – generate speech file
        tts_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        self.tts.save(final_response, tts_file)

        # Play audio and move robot concurrently
        audio_thread = threading.Thread(
            target=self.robot.audio.play_async, args=(tts_file,)
        )
        motion_thread = threading.Thread(
            target=self.action.execute, args=(final_response,)
        )
        audio_thread.start()
        motion_thread.start()
        audio_thread.join()
        motion_thread.join()
