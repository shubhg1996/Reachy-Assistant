"""Basic usage example for the ttsclient package."""

from ttsclient import TextToSpeech

tts = TextToSpeech(voice="en-GB-SoniaNeural")  # British voice

# Save to file
tts.save("Hello, this is a test.", "hello.mp3")
print("Saved to hello.mp3")

# Or speak directly (plays audio)
tts.speak("Your text has been processed.")
