#!/usr/bin/env python3
#############################################################################################################
# Example for controlling the GoPiGo using the Keyboard and obstacle avoidance
# Controls:
#   w:  Move forward
#   a:  Turn left
#   d:  Turn right
#   s:  Move back
#   x:  Stop
#   z:  Exit
# http://www.dexterindustries.com/GoPiGo/
# History
# ------------------------------------------------
# Author          Date              Comments
# William Loring  10/15/21          Created as an example, uses multithreading to add obstacle avoidance
#
# EasyGoPiGo3 documentation
# https://gopigo3.readthedocs.io/en/latest
##############################################################################################################


# ---------------------------------------- IMPORTS -------------------------------------------#
import sys                              # For sys.exit
import time                             # Import the time library for the sleep function
# Threading module to run obstacle avoidance and remote control at the same time
import threading
import easygopigo3 as easy              # Import the EasyGoPiGo3 library


# --------------------------------- INITIALIZE THE GOPIGO -------------------------------------#
gpg = easy.EasyGoPiGo3()                      # Initialize an EasyGoPiGo3 object
distance_sensor = gpg.init_distance_sensor()  # Initialize distance sensor object
servo = gpg.init_servo("SERVO1")              # Initialize servo object Port 1

# Set servo pointing straight ahead at 90 degrees
# You may have to change the degrees to adapt to your servo
# All servos line up slightly differently
# Less than 90 moves the servo to the right
# Greater than 90 moves the servo to the left
servo.rotate_servo(90)

gpg.set_speed(200)       # Set initial speed
DETECTION_DISTANCE = 12  # Distance in inches


def main():
    display_menu()
    # Create and start daemon thread for the obstacle_avoidance function
    # A daemon thread will terminate when the program terminates
    obs = threading.Thread(
        target=obstacle_detection,
        daemon=True
    )
    obs.start()

    # Main program loop
    while True:
        remote_control_console()
        # sleep is blocking code, nothing else can happen during sleep
        # For debouncing the key presses
        time.sleep(.05)


# ---------------------- REMOTE CONTROL CONSOLE --------------------------- #
def remote_control_console():
    """Remote control the GoPiGo from the console"""
    # Fetch the input from the terminal
    key_press = input("Enter the Command: ")

    # Forward
    if key_press == 'w':
        gpg.forward()

    # Turn Left
    elif key_press == 'a':
        gpg.left()

    # Turn Right
    elif key_press == 'd':
        gpg.right()

    # Backward
    elif key_press == 's':
        gpg.backward()

    # Stop when spacebar pressed
    elif key_press == ' ':
        gpg.stop()

    # Exit program
    elif key_press == 'z':
        print("Exiting")
        sys.exit()          # Exit the program
    else:
        print("Unknown Command, Please Enter Again")


# ------------------------- OBSTACLE DETECTION --------------------------- #
def obstacle_detection():
    """Obstacle detection routine, called every 500 ms"""
    while True:
        # Find the distance of the object in front
        dist = distance_sensor.read_inches()
        # print("Dist:", dist, 'inches')        # Print feedback to the console for testing

        # If the object is closer than avoidance distance,
        # call the obstacle avoidance function
        if dist < DETECTION_DISTANCE:
            obstacle_avoidance()

        time.sleep(.5)


# ------------------------- OBSTACLE AVOIDANCE --------------------------- #
def obstacle_avoidance():
    """Obstacle avoidance routine"""
    # Place any obstacle avoidance code here
    # This code is a proof of concept and a placeholder for your code
    print("Stopping")    # Print feedback to the console
    gpg.stop()           # Stop the GoPiGo


# ---------------------------- DISPLAY MENU ------------------------------ #
def display_menu():
    # os.system('cls' if os.name == 'nt' else 'clear')
    print("Console GoPiGo Robot control")
    # Menu string
    menu = "Press:\n\tw: Move GoPiGo Robot forward\n\ta: Turn GoPiGo Robot left\n\td: Turn GoPiGo Robot right\n\ts: Move GoPiGo Robot backward\nspace bar: Stop GoPiGo Robot\n\tz: Exit\n"
    print(menu)
    print(f"Speed: {gpg.get_speed()}")


# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()
