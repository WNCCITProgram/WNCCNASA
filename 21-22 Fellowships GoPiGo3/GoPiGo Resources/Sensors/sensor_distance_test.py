#!/usr/bin/env python3
"""
    Name: distance_sensor_test.py
    Purpose: Demonstrate reading the distance sensor in mm and inches
"""
# EasyGoPiGo3 documentation: https://gopigo3.readthedocs.io/en/latest
# DI sensor documentation: https://di-sensors.readthedocs.io/en/master/
# Copyright (c) 2017 Dexter Industries Released under the MIT license
#
# History
# ------------------------------------------------
# Author     Date      	    Comments
# Loring     09/25/21       Convert to EasyGoPiGo3, test with Python 3.5
#
#
#####################################################################
#
# Connect Distance Sensor to an I2C port 
#
#####################################################################
# Have a question about this example?  Ask on the forums here:
# http://forum.dexterindustries.com/c/gopigo

import time                             # Import the time library for the sleep function
import easygopigo3 as easy              # Import the GoPiGo3 library
gpg = easy.EasyGoPiGo3()                # Initialize an EasyGoPiGo3 object

# Initialize an object of the Distance Sensor class.
# I2C1 and I2C2 are just labels used for identifying the port on the GoPiGo3 board.
# Technically, I2C1 and I2C2 are the same thing, so we don't have to pass any port to the constructor.
my_distance_sensor = gpg.init_distance_sensor()


def main():
    while True:
        # Read the sensor data into millimeters and inches variables
        mm = str(my_distance_sensor.read_mm())
        inches = str(my_distance_sensor.read_inches())

        # Print the values of the sensor to the console
        print("Distance Sensor Reading: " + inches + " inches " + mm + " mm")

        # sleep is only needed to see the measurements
        # sleep is blocking code, nothing else can happen during sleep
        # Don't use in production code
        time.sleep(1)


# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()
