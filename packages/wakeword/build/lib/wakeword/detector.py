# src/wakeword/detector.py
import queue
import threading

import numpy as np
import openwakeword
import sounddevice as sd
from openwakeword.model import Model


class WakeWordDetector:
    """
    Minimal wake word detector using openWakeWord with built‑in VAD.
    """

    def __init__(self, wakeword="hey_mycroft", vad_threshold=0.35, sensitivity=0.5):
        """
        Args:
            wakeword: One of the pre-trained model names (e.g., "hey_mycroft", "alexa").
            vad_threshold: Voice activity threshold (0..1). Lower = more sensitive.
            sensitivity: Wake word detection threshold (0..1). Lower = more sensitive.
        """
        # Download models if not already cached (first run)
        openwakeword.utils.download_models()

        # Initialize model with VAD, and set the inference framework
        self.model = Model(
            wakeword_models=[wakeword],
            vad_threshold=vad_threshold,
            inference_framework="tflite",  # or "onnx" for different backend
        )

        self.wakeword_name = wakeword
        self.sensitivity = sensitivity
        self.callback = None
        self._running = False
        self._thread = None
        self._audio_queue = queue.Queue()

    def on_wake_word(self, callback):
        """Register a callback to be called when wake word is detected."""
        self.callback = callback

    def start(self):
        """Start listening in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop listening."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _listen(self):
        """Audio capture loop with VAD and wake word detection."""
        samplerate = 16000
        frames_per_chunk = 1600  # 100ms

        with sd.InputStream(
            samplerate=samplerate,
            channels=1,
            blocksize=frames_per_chunk,
            dtype=np.int16,
            callback=self._audio_callback,
        ):
            while self._running:
                try:
                    audio_chunk = self._audio_queue.get(timeout=0.1)
                    # Predict expects a numpy array and a threshold (float)
                    scores = self.model.predict(audio_chunk, threshold=self.sensitivity)
                    if scores[self.wakeword_name] > self.sensitivity:
                        if self.callback:
                            self.callback()
                except queue.Empty:
                    continue

    def _audio_callback(self, indata, frames, time, status):
        """Called by sounddevice for each audio block."""
        if status:
            print(f"Audio status: {status}")
        self._audio_queue.put(indata.copy().flatten())
