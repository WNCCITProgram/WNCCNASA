#!/usr/bin/env python3
# Filename: sensor_ir_test.py
# Purpose:# Use the IR Receiver and GoPiGo remote
#
# https://github.com/DexterInd/GoPiGo3
# EasyGoPiGo3 documentation: https://gopigo3.readthedocs.io/en/latest
# DI sensor documentation: https://di-sensors.readthedocs.io/en/master/
# Copyright (c) 2017 Dexter Industries Released under MIT license
#####################################################################
#
# Connect Grove IR receiver to port AD1
#
#####################################################################
# Results: When you run this program,
# a value will be printed that corresponds to the button being pressed on the remote.

from time import sleep # import the time library for the sleep function
import gopigo3         # import the GoPiGo3 drivers

# Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.
GPG = gopigo3.GoPiGo3()

try:
    GPG.set_grove_type(GPG.GROVE_1, GPG.GROVE_TYPE.IR_DI_REMOTE)

    while(True):
        try:
            # Print current ir remote key press
            print(GPG.get_grove_value(GPG.GROVE_1))
        except gopigo3.SensorError as error:
            print(error)
        sleep(0.05)

# except the program gets interrupted by Ctrl+C on the keyboard.
except KeyboardInterrupt:
    # Unconfigure the sensors, disable the motors,
    # restore the LED to the control of the GoPiGo3 firmware
    GPG.reset_all()
