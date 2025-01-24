#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).

# This program uses the IR Receiver
# connected to AD1 with the Go Box IR remote to drive the GoPiGo3.
# Use grove_ir.py to discover the values for the remote

from time import sleep        # Import the time library for the sleep function
import easygopigo3 as easy    # Import the EasyGoPiGo3 library

#------------------------ INITIALIZE GOPIGO -------------------------------------#
gpg = easy.EasyGoPiGo3()    # Initialize a EasyGoPiGo3 object
gpg.set_speed(200)          # Set initial speed

value_last = -1


def read_ir_keys():
    global value_last
    try:
        value = gpg.get_grove_value(gpg.GROVE_1)
        print(value)
        if value != value_last:
            value_last = value
            if value == 10: # forward
                gpg.set_motor_dps(gpg.MOTOR_LEFT,  300)
                gpg.set_motor_dps(gpg.MOTOR_RIGHT,  300)
            elif value == 12: # turn left
                gpg.set_motor_dps(gpg.MOTOR_LEFT, -150)
                gpg.set_motor_dps(gpg.MOTOR_RIGHT,  150)
            elif value == 14: # turn right
                gpg.set_motor_dps(gpg.MOTOR_LEFT,  150)
                gpg.set_motor_dps(gpg.MOTOR_RIGHT, -150)
            elif value == 16: # reverse
                gpg.set_motor_dps(gpg.MOTOR_LEFT, -300)
                gpg.set_motor_dps(gpg.MOTOR_RIGHT, -300)
            else:
                gpg.set_motor_dps(gpg.MOTOR_LEFT, 0)
                gpg.set_motor_dps(gpg.MOTOR_RIGHT, 0)
    except IOError or easygopigo3.SensorError as e:
        pass

# where program starts
def main():
    print("Use the arrows on your remote controller to control your GoPiGo3")
    print("The IR Receiver (remote sensor) should connected to port AD1")
    print("Ctrl-C to exit the program")
    
    
    gpg.set_grove_type(
        gpg.GROVE_1,
        gpg.GROVE_TYPE.IR_DI_REMOTE
    )
    while True:
        try:
            read_ir_keys()
    
        # except the program gets interrupted by Ctrl+C on the keyboard.
        except KeyboardInterrupt:
            # Unconfigure the sensors, disable the motors, and
            # restore the LED to the control of the GoPiGo3 firmware.
            gpg.reset_all()
            exit(0)
    
        except:
            pass


if __name__ == "__main__":
    main()
