#!/usr/bin/env python3
"""
    Name: sensor_bme280.py
    Purpose: Read temperature, humidity and barometric pressure
"""
# ------------------------------------------------
# History
# ------------------------------------------------
# Author    Date        Comments
# Loring    10/24/21    Convert celsius to fahrenheit, convert pressure to inHg,
#                       compensate for altitude

# Barometric pressure compensation for altitude:
# https://www.engineeringtoolbox.com/barometers-elevation-compensation-d_1812.html
#
# EasyGoPiGo3 documentation: https://gopigo3.readthedocs.io/en/latest
# DI sensor documentation: https://di-sensors.readthedocs.io/en/latest
# Copyright (c) 2017 Dexter Industries Released under the MIT license
# Python example program for either of these
# - Dexter BME280 Temperature Humidity Pressure Sensor
# - Grove BME280
#
###################################################################################
#
# Connect Temperature, Humidity, Pressure sensor (BME280 to I2C port
#
###################################################################################

from time import sleep
from di_sensors.easy_temp_hum_press import EasyTHPSensor
from easygopigo3 import EasyGoPiGo3  # Import GoPiGo3 library

# Create an instance of the GoPiGo3 class
gpg = EasyGoPiGo3()

print("Example program for reading Dexter Industries")
print("Temperature Humidity Pressure Sensor on an I2C port.")

# Initialize an EasyTHPSensor object
my_thp = EasyTHPSensor()

try:
    while True:
        # Read temperature
        # temp = my_thp.safe_celsius()
        temp = my_thp.safe_fahrenheit()

        # Read relative humidity
        hum = my_thp.safe_humidity()

        # Read pressure in pascals
        press = my_thp.safe_pressure()

        # Convert pascals to inHg, compensate for 4000' altitude
        press = (press / 3386.38867) + 4.08

        # Print values to the console
        print("Temperature: {:5.1f}F  Humidity: {:5.1f}%  Pressure: {:5.2f} inHg".format(
            temp, hum, press))

        # Pause between readings
        sleep(5)

# except the program gets interrupted by Ctrl+C on the keyboard.
except KeyboardInterrupt:
    # Unconfigure the sensors, disable the motors, and restore the LED to the control of the GoPiGo3 firmware.
    gpg.reset_all()

