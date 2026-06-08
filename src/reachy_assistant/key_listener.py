"""KeyListener listens for a key press and records audio using sounddevice."""

import numpy as np
import sounddevice as sd
from pynput import keyboard


class KeyListener:
    """Listens for a key press and records audio using sounddevice."""

    def __init__(self, record_callback, samplerate=16000):
        """Initialize the KeyListener with a record callback and optional samplerate."""
        self.record_callback = record_callback
        self.samplerate = samplerate
        self.is_recording = False
        self.audio_frames = []
        self.stream = None

    def start(self, key="space"):
        """Start listening for the specified key and record audio."""
        self.key = key
        with keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release
        ) as listener:
            listener.join()  # blocks until listener stops (never stops here)

    def _on_press(self, key):
        try:
            if hasattr(key, "name") and key.name == self.key:
                if not self.is_recording:
                    self._start_recording()
        except AttributeError:
            pass

    def _on_release(self, key):
        try:
            if hasattr(key, "name") and key.name == self.key:
                if self.is_recording:
                    self._stop_recording()
        except AttributeError:
            pass

    def _start_recording(self):
        self.is_recording = True
        self.audio_frames = []
        self.stream = sd.InputStream(
            samplerate=self.samplerate, channels=1, callback=self._audio_callback
        )
        self.stream.start()
        print("Recording started...")

    def _stop_recording(self):
        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        recording = np.concatenate(self.audio_frames, axis=0)
        print("Recording finished.")
        self.record_callback(recording)

    def _audio_callback(self, indata, frames, time, status):
        self.audio_frames.append(indata.copy())
