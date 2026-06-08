from reachy_mini_lib import ReachyRobot

with ReachyRobot() as robot:
    robot.wake_up()
    robot.set_head(pitch_deg=20, yaw_deg=30, duration=0.8)
    robot.set_antennas(right_deg=45, left_deg=-20, duration=0.5)
    robot.set_body_yaw(15, duration=0.5)
    robot.wait(1.5)
    robot.play_move("dance1")  # needs internet first time
    robot.goto_sleep_pose()
