#!/usr/bin/env python3
# Filename: sensor_imu_test.py
# Purpose: Example program for Dexter Inertial Measurement Unit (IMU) sensor
# It detects motion, orientation, and position of your robot
# Compass, accelerometer, gyroscope, temperature
# The sensor has 9 degrees of freedom (9-DOF)
# provides an accurate and high-speed orientation of your robot.
# The sensor has a built in compass, accelerometer, and gyroscope.
# You can use these to tell which compass direction your robot is turned to,
# how fast it is turning, what angle it is to the ground, and how fast it is changing speed.
#
# EasyGoPiGo3 documentation: https://gopigo3.readthedocs.io/en/latest
# DI sensor documentation: https://di-sensors.readthedocs.io/en/master/
# Copyright (c) 2017 Dexter Industries Released under the MIT license
#
# History
# ------------------------------------------------
# Author     Date           Comments
# Loring     10/30/21       Change to I2C bus
#

##############################################################################
#
# Connect IMU sensor to I2C port
#
##############################################################################
from time import sleep  # For sleep function

from di_sensors.easy_inertial_measurement_unit import EasyIMUSensor
# For reading temperature, EasyIMUSensor doesn't read temperature
from di_sensors.inertial_measurement_unit import InertialMeasurementUnit

from easygopigo3 import EasyGoPiGo3  # Import GoPiGo3 library
gpg = EasyGoPiGo3()  # Initialize an EasyGoPiGo3 object
print("Reading Dexter Industries IMU Sensor on a GoPiGo3 I2C port.")

easy_imu = EasyIMUSensor(port="I2C")
# Initialize IMU object on I2C bus: RPI_1SW to read temperature
imu = InertialMeasurementUnit(bus="RPI_1SW")

try:
    print("Calibrating the IMU . . . . please be patient . . .")
    easy_imu.safe_calibrate()    # Allow time for sel fcalibration
    while True:
        # Read the magnetometer, gyroscope, accelerometer, euler, and temperature values
        mag = easy_imu.safe_read_magnetometer()
        # Get true north in degrees
        true_north_degrees = easy_imu.safe_north_point()
        # Convert degrees to heading
        true_north_heading = easy_imu.convert_heading(true_north_degrees)
        gyro = easy_imu.safe_read_gyroscope()
        accel = easy_imu.safe_read_accelerometer()
        euler = easy_imu.safe_read_euler()
        # IMU reads temp in celsius
        temp_c = imu.read_temperature()
        # Convert to Fahrenheit
        temp_f = (temp_c * 9.0) / 5.0 + 32

        string_to_print = "Magnetometer X: {:.1f}  Y: {:.1f}  Z: {:.1f} \n" \
            "Gyroscope X: {:.1f}  Y: {:.1f}  Z: {:.1f} \n" \
            "Accelerometer X: {:.1f}  Y: {:.1f} Z: {:.1f} \n" \
            "Euler Heading: {:.1f}  Roll: {:.1f}  Pitch: {:.1f} \n" \
            "Temperature F: {:.1f}F \n" \
            "Heading: {}\n".format(mag[0], mag[1], mag[2],
                                   gyro[0], gyro[1], gyro[2],
                                   accel[0], accel[1], accel[2],
                                   euler[0], euler[1], euler[2],
                                   temp_f, true_north_heading)
        # Print all IMU readings
        print(string_to_print)

        sleep(1)

# The program gets interrupted by Ctrl+C on the keyboard
except KeyboardInterrupt:
    # Unconfigure the sensors, disable the motors
    # Restore the LED's to the control of the GoPiGo3 firmware
    gpg.reset_all()
