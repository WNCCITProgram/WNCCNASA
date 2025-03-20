#!/usr/bin/env python3
#
# History
# ------------------------------------------------
# Author     Date      	    Comments
# Loring     09/12/21       Example of motor control with Python
#
# This code is an example for controlling the GoPiGo3 motors.
# EasyGoPiGo3 documentation: https://gopigo3.readthedocs.io/en/latest
# Copyright (c) 2017 Dexter Industries Released under the MIT license

from time import sleep      # Import the time library for the sleep function
import easygopigo3 as easy  # Import the GoPiGo3 library
gpg = easy.EasyGoPiGo3()    # Initialize a EasyGoPiGo3 object
gpg.set_speed(200)          # Set initial speed
SLEEP_2_SECOND = 2
SLEEP_1_SECOND = 1


def main():

    # Print the current speed
    print(str(gpg.get_speed()))
    sleep(SLEEP_1_SECOND)

    print("Move the motors forward freely for 2 seconds.")
    gpg.forward()
    sleep(SLEEP_2_SECOND)
    # Stop both motors
    gpg.stop()

    print("Stop the motors for 1 second.")
    sleep(SLEEP_2_SECOND)

    print("Drive the motors forward 12 inches and then stop.")
    gpg.drive_inches(12)
    sleep(SLEEP_2_SECOND)

    print("Turn right for 1 second.")
    gpg.right()
    sleep(SLEEP_1_SECOND)

    print("Turn left for 1 second.")
    gpg.left()
    sleep(SLEEP_1_SECOND)

    print("Spin left for 2 seconds.")
    gpg.spin_left()
    sleep(SLEEP_2_SECOND)

    print("Spin right for 2 seconds.")
    gpg.spin_right()
    sleep(SLEEP_2_SECOND)

    print("Turn left 180 degrees.")
    gpg.turn_degrees(-180)

    print("Turn right 180 degrees.")
    gpg.turn_degrees(180)

    print("Orbit right for 360 degrees around a 20 cm diameter.")
    gpg.orbit(360, 20)

    print("Stop!")
    gpg.stop()
    print("Done!")


# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()
