#!/usr/bin/env python3
#
# https://github.com/DexterInd/GoPiGo3
#
# History
# ------------------------------------------------
# Author     	Date      		Comments
# Loring        09/14/21        Converted to Python3
#
# This code is an example for controlling the GoPiGo3 blinkers.
# These "Blinkers" are the LED's are located under the I2C ports on the front of the  GoPiGo3
#
# EasyGoPiGo3 documentation: https://gopigo3.readthedocs.io/en/latest
# Copyright (c) 2017 Dexter Industries Released under the MIT license
#
# Results:  The GoPiGo3 will turn both LED's on, then the left LED off,
# and then the right LED off.

import time                 # Import the time library for the sleep function
import easygopigo3 as easy  # Import the GoPiGo3 library
gpg = easy.EasyGoPiGo3()    # Create an EasyGoPiGo3 object


def main():
    while True:
        # Turn both Blinker LEDs on
        # The Blinker are located under the I2C ports on the fron of the GoPiGo3
        print("Both LED's on")
        gpg.led_on("left")
        gpg.led_on("right")

        # Wait .5 second
        time.sleep(.5)

        # Turn the left LED off
        print("Right LED on, Left LED off")
        gpg.led_off("left")
        time.sleep(.5)

        # Turn the right LED Off
        print("Left LED on, Right LED off")
        gpg.led_off("right")
        time.sleep(.5)


# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()
