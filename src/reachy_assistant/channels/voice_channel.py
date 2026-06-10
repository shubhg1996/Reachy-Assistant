"""OpenClaw Voice Surface: Overhauled with state-aware muting to prevent self-triggering loops."""

import tempfile
import threading
import time

import numpy as np
import sounddevice as sd
import soundfile as sf
from speech2text import Speech2Text
from ttsclient import TextToSpeech
from wakeword import WakeWordDetector


class VoiceChannel:
    def __init__(
        self, agent_runtime, robot, stt_model="base", tts_voice="en-US-JennyNeural"
    ):
        self.runtime = agent_runtime
        self.robot = robot

        self.stt = Speech2Text(model_name=stt_model)
        self.tts = TextToSpeech(voice=tts_voice)

        self.wake_detector = WakeWordDetector(
            wakeword="hey_mycroft", vad_threshold=0.35, sensitivity=0.5
        )
        self.wake_detector.on_wake_word(self._on_wake_word_signal)

        self.command_event = threading.Event()
        self.is_processing = False
        self._running = False

        # Hardware Mute Lock: Tracks if the local speaker is currently pushing audio waves
        self.is_speaking = False

    def listen(self):
        """Starts the voice loop if the global system state permits it."""
        if self._running:
            return
        self._running = True

        # Check our central OpenClaw JSON state object!
        # If the user or bot turned off voice out, we can choose to keep the wake engine completely dark
        if not self.runtime.state.get("voice_out_enabled", False):
            print(
                "[Channel: Voice] System boot state is TEXT-ONLY. Leaving wake word engine offline."
            )
            return

        print("[Channel: Voice] Activating openWakeWord background engine...")
        self.wake_detector.start()
        threading.Thread(target=self._channel_loop, daemon=True).start()

    def stop(self):
        self._running = False
        self.wake_detector.stop()
        self.command_event.set()

    def _on_wake_word_signal(self):
        """Signal hook triggered asynchronously by the openWakeWord thread pool."""
        # CRITICAL HARDWARE GUARD: If the robot is currently talking or processing,
        # drop the wake signal instantly so it can never trigger itself.
        if self.is_speaking or self.is_processing:
            print(
                "[Channel: Voice] Blocked ambient wake word trigger: Robot is currently outputting audio."
            )
            return

        if not self.is_processing:
            print(
                "\n🔊 [Channel: Voice] Pure external wake word matched! Signaling loop..."
            )
            self.is_processing = True
            self.command_event.set()

    def _channel_loop(self):
        """Isolated operational channel tracking loop."""
        while self._running:
            self.command_event.wait()
            if not self._running:
                break

            try:
                # Double check modal locks right before opening mic stream
                if not self.runtime.state.get("voice_out_enabled", False):
                    print(
                        "[Channel: Voice] State changed to text-only mid-loop. Canceling wake processing."
                    )
                    break

                # Suspend background window to free up CoreAudio locks
                self.wake_detector.stop()
                self._handle_voice_turn()

            except Exception as e:
                print(f"[Channel: Voice] Runtime exception during loop processing: {e}")
            finally:
                time.sleep(0.4)  # Drain remaining hardware buffer resonance
                self.is_processing = False
                self.command_event.clear()

                # Only restart the wake word listener if the system is still in voice mode
                if self._running and self.runtime.state.get("voice_out_enabled", False):
                    self.wake_detector.start()

    def _handle_voice_turn(self):
        audio_np = self._record_audio(duration=4.0, samplerate=16000)
        if audio_np is None:
            return

        rms = np.sqrt(np.mean(audio_np.astype(np.float32) ** 2))
        if rms <= 0.01:
            return

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sf.write(tmp.name, audio_np, 16000)
            tmp_path = tmp.name

        user_text = self.stt.transcribe(tmp_path)
        if not user_text.strip():
            return
        print(f"[Voice In] -> {user_text}")

        agent_reply = self.runtime.run_turn(user_text)
        print(f"[Voice Out] <- {agent_reply}")

        # Pristine textual delivery without structural markdown leaks
        if agent_reply and self.runtime.state.get("voice_out_enabled", False):
            self.send(agent_reply)

    def send(self, text: str):
        """Converts text to speech and safely locks hardware vectors while outputting."""
        # 1. Engage Mute Lock
        self.is_speaking = True

        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tts_file = tmp.name

            self.tts.save(text, tts_file)
            print(
                f"[Channel: Voice] Streaming audio synthesis through Reachy speaker..."
            )

            # This blocks this thread while sounddevice plays audio
            self.robot.audio.play(tts_file)

        finally:
            # 2. Release Mute Lock after audio thread cleanly finishes execution
            # This guarantees that even if there is residual echo in the room, it is safe to listen again.
            time.sleep(0.2)
            self.is_speaking = False
