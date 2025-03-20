#!/usr/bin/env python3
# EasyGoPiGo3 documentation: https://gopigo3.readthedocs.io/en/latest
#
########################################################################
# This example demonstrates using the distance sensor with the GoPiGo
# In this examples, the GoPiGo keeps reading from the distance sensor
# When it close to the an obstacle, it stops.
#
# http://www.dexterindustries.com/GoPiGo/
# Copyright (c) 2017 Dexter Industries Released under the MIT license
# History
# ------------------------------------------------
# Author     Date      		Comments
# Karan      21 Aug 14 		Initial Authoring
# Loring     10/12/21           Convert to EasyGoPiGo3, test with Python 3.5
#
########################################################################
#
# ! Attach Distance sensor to I2C Port.
#
########################################################################

#--------------------------------- IMPORTS -------------------------------------#
import time                                   # Import time library for sleep function
import easygopigo3 as easy                    # Import the GoPiGo3 library
gpg = easy.EasyGoPiGo3()                      # Create a EasyGoPiGo3 object
# Initialize a distance sensor object
distance_sensor = gpg.init_distance_sensor()
# Initialize a servo object on Servo Port 1
servo = gpg.init_servo("SERVO1")

# Set servo pointing straight ahead at 90 degrees
# You may have to change the degrees to adapt to your servo
# All servos line up slightly differently
# Less than 90 moves the servo to the right
# Greater than 90 moves the servo to the left
servo.rotate_servo(90)
gpg.set_speed(200)       # Set initial speed
AVOIDANCE_DISTANCE = 12  # Distance in inches from obstacle where the GoPiGo should stop


def main():
    print("Press ENTER to start")
    input()        # Wait for input to start

    gpg.forward()   # Start moving forward, GoPiGo will continue moving forward until it receives another movement command
    running = True  # Boolean/flag to control the while loop

    while running == True:                    # Loop while running == True
        dist = distance_sensor.read_inches()  # Find the distance of the object in front
        print("Dist:", dist, 'inches')        # Print feedback to the console
        # If the object is closer than the "distance_to_stop" distance, stop the GoPiGo
        if dist < AVOIDANCE_DISTANCE:
            print("Stopping")                 # Print feedback to the console
            gpg.stop()                        # Stop the GoPiGo
            running = False                   # Set running to false to break out of the loop

        # sleep is blocking code, nothing else can happen during sleep
        time.sleep(.1)  # 100 milliseconds


# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()
