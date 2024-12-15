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
# Loring     01/30/22       Comment code, add constants for IR Codes

# This program uses the IR Receiver
# connected to AD1 IR remote to drive the GoPiGo3
# Use grove_ir.py to discover the values for the remote

from Joann.ir_rc_console_sons_driving_school import rectangle
import easygopigo3 as easy    # Import the EasyGoPiGo3 library
import ir_rc_console_sons_driving_school

#------------------------ INITIALIZE GOPIGO -------------------------------------#
gpg = easy.EasyGoPiGo3()    # Initialize a EasyGoPiGo3 object
gpg.set_speed(200)          # Set initial speed

# Constants for IR Codes
# Use grove_ir.py to discover values for your remote
FORWARD = 10
LEFT = 12
RIGHT = 14
BACKWARD = 12
SQUARE = 1
RECTANGLE = 2
SENTRY = 3
RETRACE = 4
FORWAR_DREVERSE = 5
OCTAGON = 6
EQUILATERAL_TRIANGLE = 7
FIVE_POINT_STAR = 8


value_last = -1

# Setup Grove IR sensor to receive remote codes
gpg.set_grove_type(
    gpg.GROVE_1,
    gpg.GROVE_TYPE.IR_DI_REMOTE
)


def main():
    print("Use the arrows on your remote controller to control your GoPiGo3")
    print("The IR Receiver (remote sensor) should connected to port AD1")
    print("Ctrl-C to exit the program")

    while True:
        try:
            read_ir_keys()

        # Except the program gets interrupted by Ctrl+C on the keyboard.
        except KeyboardInterrupt:
            # Unconfigure the sensors, disable the motors, and
            # restore the LED to the control of the GoPiGo3 firmware.
            gpg.reset_all()
            exit(0)
        except:
            print("Sorry, there was an error")


def read_ir_keys():
    global value_last
    try:
        # Get value from IR remote
        value = gpg.get_grove_value(gpg.GROVE_1)
        if value != value_last:
            value_last = value
            # Forward
            if value == FORWARD:
                gpg.forward()
            # Left
            elif value == LEFT:
                gpg.left()
            # Right
            elif value == RIGHT:
                gpg.right()
            # Reverse
            elif value == BACKWARD:
                gpg.backward()
            elif value == SQUARE:
                ir_rc_console_sons_driving_school.square()
            elif value == RECTANGLE:
                ir_rc_console_sons_driving_school.rectangle()
            elif value == SENTRY:
                ir_rc_console_sons_driving_school.sentry()
            elif value == RETRACE:
                ir_rc_console_sons_driving_school.retrace()
            elif value == FORWAR_DREVERSE:
                ir_rc_console_sons_driving_school.forwardReverse()
            elif value == OCTAGON:
                ir_rc_console_sons_driving_school.octagon()
            elif value == EQUILATERAL_TRIANGLE:
                ir_rc_console_sons_driving_school.equilateralTriangle()
            elif value == FIVE_POINT_STAR:
                ir_rc_console_sons_driving_school.fivePointStar()
            # Stop
            else:
                gpg.stop()

    except IOError or easygopigo3.SensorError as e:
        # Print error
        print(e)


# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()
