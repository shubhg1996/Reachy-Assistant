"""Audio recorder for Reachy Mini using directional microphones or system microphone fallback."""

import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.io.wavfile import write as write_wav


class AudioRecorder:
    """Audio recorder for Reachy Mini using directional microphones or system microphone fallback."""

    def __init__(self, media_backend="no_media"):
        """Initialize AudioRecorder with the specified media backend."""
        self._media_backend = media_backend

    def record(
        self,
        duration=5.0,
        filename="recording.wav",
        samplerate=16000,
        device=None,
        use_fallback_mic=True,
    ):
        """Record audio from Reachy Mini's directional microphones.

        If robot mic not found and use_fallback_mic=True, uses the default system microphone.
        """
        if device is None:
            devices = sd.query_devices()
            # Look for Reachy Mini audio input
            reachy_devices = [
                i
                for i, d in enumerate(devices)
                if d["max_input_channels"] > 0 and "Reachy" in d["name"]
            ]
            if reachy_devices:
                device = reachy_devices[0]
                print(f"Using Reachy Mini microphone: {devices[device]['name']}")
            elif use_fallback_mic:
                # Find any system input device (prefer non-virtual, non-iPhone)
                for i, d in enumerate(devices):
                    if (
                        d["max_input_channels"] > 0
                        and "iPhone" not in d["name"]
                        and "Zoom" not in d["name"]
                    ):
                        device = i
                        print(
                            f"⚠️ Reachy mic not found. Falling back to system mic: {devices[device]['name']}"
                        )
                        break
                if device is None:
                    # Last resort: default input device
                    device = sd.default.device[0]
                    if device is None:
                        raise RuntimeError(
                            "No input device available. Please check your microphone settings."
                        )
            else:
                raise RuntimeError(
                    "No Reachy Mini audio device found. Is the robot connected and powered?"
                )

        print(f"Recording for {duration} seconds...")
        recording = sd.rec(
            int(duration * samplerate), samplerate=samplerate, channels=1, device=device
        )
        sd.wait()
        write_wav(filename, samplerate, (recording * 32767).astype(np.int16))
        print(f"Saved to {filename}")

    def play(self, filepath, device=None, use_fallback_speaker=True):
        """Play an audio file through Reachy's speakers (if available).

        filepath: Path to WAV or MP3 file (MP3 requires soundfile >= 0.12.0)
        device: Optional specific output device name or index
        use_fallback_speaker: If True and Reachy speaker not found, use system default
        """
        self.play_async(
            filepath, device=device, use_fallback_speaker=use_fallback_speaker
        )
        sd.wait()  # Wait until playback finishes
        print("Playback complete.")

    def play_async(self, filepath, device=None, use_fallback_speaker=True):
        """Play an audio file asynchronously through Reachy's speakers (if available).

        filepath: Path to WAV or MP3 file (MP3 requires soundfile >= 0.12.0)
        device: Optional specific output device name or index
        use_fallback_speaker: If True and Reachy speaker not found, use system default
        """
        # Load audio (supports WAV, MP3, etc. via soundfile)
        data, samplerate = sf.read(filepath, dtype="float32")

        # Convert to stereo if mono (common for speakers)
        if data.ndim == 1:
            data = np.column_stack((data, data))

        # Select output device
        if device is None:
            devices = sd.query_devices()
            # Look for Reachy audio output
            reachy_outputs = [
                i
                for i, d in enumerate(devices)
                if d["max_output_channels"] > 0 and "Reachy" in d["name"]
            ]
            if reachy_outputs:
                device = reachy_outputs[0]
                print(f"Using Reachy speaker: {devices[device]['name']}")
            elif use_fallback_speaker:
                device = sd.default.device[1]  # default output
                print(
                    f"⚠️ Reachy speaker not found. Falling back to system speaker: {devices[device]['name']}"
                )
            else:
                raise RuntimeError(
                    "No Reachy audio output device and fallback disabled"
                )

        print(f"Playing {filepath}...")
        sd.play(data, samplerate, device=device)
        return
