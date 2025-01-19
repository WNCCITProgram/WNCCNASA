#!/usr/bin/env python3
#
# https://github.com/DexterInd/GoPiGo3
#
#
# History
# ------------------------------------------------
# Author        Date            Comments
# Loring        09/14/21        Converted to Python3
#
# EasyGoPiGo3 documentation: https://gopigo3.readthedocs.io/en/latest
# Copyright (c) 2017 Dexter Industries Released under the MIT license
#
# This code is an example for controlling the GoPiGo3 eyes
# The eyes are located on the top of the GoPiGo and show as the eyes of the robot
# Results:  The GoPiGo3 will turn the eyes on with different colors

from time import sleep           # Import the time library for the sleep function
import atexit                    # Used to close eyes when program exits
import easygopigo3 as easy       # Import the GoPiGo3 library
gpg = easy.EasyGoPiGo3()         # Create an EasyGoPiGo3 object
atexit.register(gpg.close_eyes)  # When the program exits, turn off both eyes

# Setting the eye color is a tuple of (R, G, B) values,
# The range is 0-254. Set constants to RGB colors
RED = (80, 1, 1)
GREEN = (1, 80, 1)
BLUE = (1, 1, 80)
SLEEP = .5


def main():
    print("Press CTRL C to exit the program")
    while True:
        # Set the color for both eyes
        gpg.set_left_eye_color((BLUE))
        gpg.set_right_eye_color((BLUE))

        # Open the left eye, displays the color
        gpg.open_left_eye()
        # sleep to allow the LED to show
        sleep(SLEEP)

        # Open the right eye, displays the color
        gpg.open_right_eye()
        sleep(SLEEP)

        # Set BOTH eye color to red.
        gpg.set_eye_color(RED)

        # Change the left eye to red
        gpg.open_left_eye()
        sleep(SLEEP)

        # Change the right eye to red
        gpg.open_right_eye()
        sleep(SLEEP)

        # Close both eyes
        gpg.close_eyes()
        sleep(SLEEP)

        # Set the left eye to green, the right eye to blue.
        gpg.set_left_eye_color(GREEN)
        gpg.set_right_eye_color(BLUE)

        # Open both eyes at once
        gpg.open_eyes()
        leep(SLEEP)


# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()
