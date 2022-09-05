#!/usr/bin/env python3
#
# https://github.com/DexterInd/GoPiGo3
#
# EasyGoPiGo3 documentation: https://gopigo3.readthedocs.io/en/latest
# Copyright (c) 2017 Dexter Industries Released under the MIT license
#
# Original program from GoPiGo3 file system, or https://github.com/DexterInd/GoPiGo3
# /Dexter/Software/Python/Examples/Servo.py
#
# History
# ------------------------------------------------
# Author     Date      	    Comments
# Loring     09/12/21       Convert to EasyGoPiGo3, test with Python 3.5
#
# This code is an example for controlling the GoPiGo3 Servos
#
# Results:  When you run this program, the GoPiGo3 Servos will rotate back and forth.


#--------------------------------- IMPORTS -------------------------------------#
from time import sleep            # Import the time library for the sleep function
import easygopigo3 as easy        # Import the GoPiGo3 library


#--------------------------------- INITIALIZE GOPIGO -------------------------------------#
gpg = easy.EasyGoPiGo3()          # Initialize EasyGoPiGo3 object
servo = gpg.init_servo("SERVO1")  # Initialize servo object on Servo Port 1

# Set servo pointing straight ahead at 90 degrees
# You may have to change the degrees to adapt to your servo
# All servos line up slightly differently
servo.rotate_servo(90)
print("Forward")
sleep(1)


#--------------------------------- MAIN PROGRAM -------------------------------------#
def main():
    # Right
    print("Right")
    servo.rotate_servo(30)
    sleep(1)

    # Left
    print("Left")
    servo.rotate_servo(150)
    sleep(1)

    # Forward
    print("Forward")
    servo.rotate_servo(90)
    sleep(1)

    # Disable or "float" the servo
    servo.disable_servo()


# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()
