"""Record audio from Reachy Mini's directional microphones and save to a WAV file."""

from reachy_mini_lib import ReachyRobot

# For audio capture we need media backend enabled (default or "gstreamer").
# But sounddevice accesses the USB audio directly, so media_backend can stay "no_media".
with ReachyRobot(media_backend="no_media") as robot:
    # Optional: wake up (not required for audio)
    robot.torque.wake_up()

    # Record 5 seconds and save
    robot.audio.record(duration=5.0, filename="my_recording.wav", samplerate=16000)

    # play back the recording using the robot's speakers
    robot.audio.play("my_recording.wav")

    robot.torque.go_to_sleep()
