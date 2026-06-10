import numpy as np
import sounddevice as sd

print("Default input device:", sd.default.device)
print("Available input devices:")
for i, dev in enumerate(sd.query_devices()):
    if dev["max_input_channels"] > 0:
        print(f"  {i}: {dev['name']}")

print("Recording 2 seconds...")
rec = sd.rec(int(2 * 16000), samplerate=16000, channels=1, dtype="float32")
sd.wait()
print("Recording finished, mean amplitude:", np.abs(rec).mean())
