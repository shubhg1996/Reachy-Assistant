"""Test the ActionMapper and emotion playback in isolation."""

from reachy_assistant.action_mapper import ActionMapper
from reachy_mini_lib import ReachyRobot, wait

print("1. Connecting to robot...")
with ReachyRobot() as robot:
    print("2. Waking up motors...")
    robot.torque.wake_up()

    # Test a specific emotion directly
    test_emotion = "cheerful1"  # from the available list
    print(f"3. Playing emotion: {test_emotion}")
    try:
        robot.moves.play_move(test_emotion)
        print("   Emotion played successfully.")
    except Exception as e:
        print(f"   ERROR playing emotion: {e}")
        raise

    # Test the ActionMapper with a sample LLM response
    mapper = ActionMapper(robot)
    test_responses = [
        "I am so happy to see you!",
        "This is really sad news.",
        "Wow, I'm surprised!",
        "No, I don't think so.",
    ]

    for response in test_responses:
        print(f"\n4. Testing response: '{response}'")
        mapper.execute(response)
        wait(1.5)  # let the emotion play

    print("\n5. Returning to sleep pose...")
    robot.torque.goto_sleep_pose()
