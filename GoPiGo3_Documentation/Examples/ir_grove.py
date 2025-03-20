#!/usr/bin/env python3
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# History
# ------------------------------------------------
# Author     Date           Comments
# Loring     01/30/22       Comment code
#
# This code is an example for using
# the GoPiGo3 with the IR Receiver and remote
#
# Hardware: Connect a grove IR receiver to port AD1.
#
# Results: When you run this program,
# a value will be printed that corresponds
# to the button being pressed on the remote

# -------------------------- IMPORTS ------------------------------------- #
from time import sleep      # From the time library import sleep function
import easygopigo3 as easy  # Import the EasyGoPiGo3 library

# ----------------------- INITIALIZE GOPIGO ------------------------------ #
gpg = easy.EasyGoPiGo3()    # Initialize a EasyGoPiGo3 object


def main():
    try:
        # Setup grove IR Sensor for reception
        gpg.set_grove_type(
            gpg.GROVE_1,
            gpg.GROVE_TYPE.IR_DI_REMOTE
        )

        while (True):
            try:
                # Get and print value from IR Remote
                print(gpg.get_grove_value(gpg.GROVE_1))
            except easygopigo3.SensorError as error:
                # Handle and print error
                print(error)
            # 150 ms key debounce
            sleep(0.15)

    # Except the program gets interrupted by Ctrl+C on the keyboard.
    except KeyboardInterrupt:
        # Unconfigure the sensors, disable the motors,
        # and restore the LED to the control of the GoPiGo3 firmware.
        gpg.reset_all()


main()
