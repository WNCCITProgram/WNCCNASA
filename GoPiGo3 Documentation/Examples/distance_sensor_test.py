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
# Loring     09/25/21       Convert to EasyGoPiGo3, test with Python 3.7
#

# Import the GoPiGo3 library
import easygopigo3 as easy

# Initialize an EasyGoPiGo3 object
gpg = easy.EasyGoPiGo3()

# Initialize an object of the Distance Sensor class.
# Connect to AD1 or AD2
my_distance_sensor = gpg.init_distance_sensor("AD1")

try:
    print("Press CTRL+C to stop the program")

    while True:
        # Read the sensor data into millimeters and inches
        mm = my_distance_sensor.read_mm()
        inches = my_distance_sensor.read_inches()

        # Calculate the number of feet by performing
        # integer division on inches by 12
        feet = inches // 12

        # Calculate the remaining inches by finding the
        # modulus of inches by 12
        remaining_inches = inches % 12

        # Print the values of the sensor to the console
        print(f'Distance: {mm} mm  {inches:.0f}"', end="")
        print(f"  {feet:.0f}' {remaining_inches:.0f}\"")

except KeyboardInterrupt:
    gpg.reset_all()
    exit()
