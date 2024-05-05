#!/usr/bin/env python3
# Filename: sensor_light_color_test.py
# Purpose: Python example program for the Dexter Industries Light Color Sensor
#
# EasyGoPiGo3 documentation: https://gopigo3.readthedocs.io/en/latest
# DI sensor documentation: https://di-sensors.readthedocs.io/en/master/
# Copyright (c) 2017 Dexter Industries Released under the MIT license

##############################################################################
#
# Connect Light Color Sensor to I2C port
#
##############################################################################

from time import sleep
from di_sensors.easy_light_color_sensor import EasyLightColorSensor
from easygopigo3 import EasyGoPiGo3  # Import GoPiGo3 library

gpg = EasyGoPiGo3()  # Initialize an EasyGoPiGo3 object
# Initialize a Light Color Sensor object
my_lcs = EasyLightColorSensor(led_state=True)

print("Read Dexter Light Color Sensor on an I2C port.")

try:
    while True:
        # Read the R, G, B, C color values
        red, green, blue, clear = my_lcs.safe_raw_colors()

        # Print the values
        print("Red: {:5.3f} Green: {:5.3f} Blue: {:5.3f} Clear: {:5.3f}".format(
            red, green, blue, clear))

        # Read every 200 ms, debounce the remote keys
        sleep(0.2)


# The program gets interrupted by Ctrl+C on the keyboard
except KeyboardInterrupt:
    # Unconfigure the sensors, disable the motors
    # Restore the LED's to the control of the GoPiGo3 firmware
    gpg.reset_all()
