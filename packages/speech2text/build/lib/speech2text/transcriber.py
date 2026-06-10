"""Speech-to-text transcriber using the Whisper model."""

import whisper


class Speech2Text:
    """Speech-to-text transcriber using the Whisper model."""

    def __init__(self, model_name="base"):
        """Initialize the Speech2Text transcriber with the specified model."""
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_path):
        """Transcribe the audio file at the given path and returns the text."""
        result = self.model.transcribe(audio_path)
        return result["text"]
