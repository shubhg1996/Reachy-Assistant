from wakeword import WakeWordDetector


def on_wake():
    print("🔊 Wake word detected!")


def main():
    detector = WakeWordDetector(
        wakeword="hey_mycroft",  # try also "alexa", "hey_google", etc.
        vad_threshold=0.35,
        sensitivity=0.5,
    )
    detector.on_wake_word(on_wake)
    print("Listening for 'hey mycroft'... (Ctrl+C to stop)")
    detector.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        detector.stop()
        print("Stopped.")


if __name__ == "__main__":
    main()
