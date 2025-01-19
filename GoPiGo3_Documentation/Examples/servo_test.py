#!/usr/bin/env python3
"""
    Filename: servo_test.py
    Description: Test servo movements
"""

# Import the time library for the sleep function
import time
# Import the GoPiGo3 library
import easygopigo3 as easy

# Initialize EasyGoPiGo3 object
gpg = easy.EasyGoPiGo3()

# Initialize servo object on Servo Port 1, left side of GoPiGo
servo = gpg.init_servo("SERVO1")

# Set servo pointing straight ahead at 90 degrees
# You may have to change the degrees to adapt to your servo
# All servos line up slightly differently
FORWARD = 80
LEFT = FORWARD + 55
RIGHT = FORWARD - 55


# ---------------------- MAIN PROGRAM ------------------------------------ #
def main():
    # Forward
    servo.rotate_servo(FORWARD)
    print("Forward")
    time.sleep(1)

    # Right
    print("Right")
    servo.rotate_servo(RIGHT)
    time.sleep(1)

    # Left
    print("Left")
    servo.rotate_servo(LEFT)
    time.sleep(1)

    # Forward
    print("Forward")
    servo.rotate_servo(FORWARD)
    time.sleep(1)

    # Disable or "float" the servo
    servo.disable_servo()

    # Reset all sensors and motors
    gpg.reset_all()


# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()
