"""Application entry point to execute the OpenClaw-refactored Reachy Assistant."""

import os
import sys

from reachy_assistant.gateway import Gateway


def main():
    print("=====================================================")
    print("   Initializing shubhg1996 Reachy Assistant v0.2.0   ")
    print("=====================================================")

    # Initialize the centralized orchestration plane
    gateway = Gateway()

    try:
        with (
            gateway.robot
        ):  # Standard wrapper context ensures lower-level SDK protection
            gateway.initialize()
            gateway.run()
    except KeyboardInterrupt:
        print(
            "\n\n[Main] Caught Ctrl+C. Parking Reachy and safely tearing down hardware..."
        )
        try:
            gateway.shutdown()
        except Exception as e:
            print(f"[Main] Ignored minor error during shutdown: {e}")
        # Force the OS to kill all zombie C-extensions and return the terminal
        os._exit(0)
    except Exception as e:
        print(f"\n[Fatal Core Crash] Unhandled system fault: {e}")
        try:
            gateway.shutdown()
        except:
            pass
        os._exit(1)


if __name__ == "__main__":
    main()
