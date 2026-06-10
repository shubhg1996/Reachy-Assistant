# test_record.py
import queue

import numpy as np
import sounddevice as sd
import soundfile as sf


def record_audio(duration=4.0, samplerate=16000):
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
        # Compute RMS to see if there is speech
        rms = np.sqrt(np.mean(audio_np**2))
        print(f"RMS amplitude: {rms:.5f} (typical speech > 0.01)")
        # Save to file for listening
        audio_int16 = (audio_np * 32767).astype(np.int16)
        sf.write("test_recording.wav", audio_int16, samplerate)
        print("Saved to test_recording.wav")
        return audio_int16

    except Exception as e:
        print(f"Recording error: {e}")
        if "stream" in locals():
            stream.stop()
            stream.close()
        return None


if __name__ == "__main__":
    print("Testing recording... Speak after the beep? (wait for prompt)")
    input("Press Enter to start recording (then speak)...")
    audio = record_audio(duration=4.0)  # change to 4.0
    if audio is not None:
        print(f"Recorded {len(audio)} samples, {len(audio) / 16000:.2f} seconds")
