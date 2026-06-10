"""Basic usage example of the Speech2Text transcriber."""

from speech2text import Speech2Text

# 1. Initialize the transcriber (downloads model on first run)
stt = Speech2Text(model_name="tiny")  # try "tiny", "small", "medium", "large"

# 2. Transcribe an audio file
audio_file = "conversation.wav"  # change this
text = stt.transcribe(audio_file)

# 3. Print result
print("Transcription:")
print(text)
