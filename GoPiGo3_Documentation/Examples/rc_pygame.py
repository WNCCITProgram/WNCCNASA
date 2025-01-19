#!/usr/bin/env python3
############################################################################
# Basic example for controlling the GoPiGo using the Keyboard
# Contributed by casten on Gitub https://github.com/DexterInd/GoPiGo/pull/112
#
# EasyGoPiGo3 documentation: https://gopigo3.readthedocs.io/en/latest
# Copyright (c) 2017 Dexter Industries Released under the MIT license
#
# This code lets you control the GoPiGo from the VNC or Pi Desktop
# These are non-blocking calls so it is much more easier to use
#
# Controls:
#   w:  Move forward
#   a:  Turn left
#   d:  Turn right
#   s:  Move back
#   x:  Stop
#   l:  Spin left
#   r:  Spin right
#   t:  Increase speed
#   g:  Decrease speed
#   z:  Exit
# ------------------------------------------------
# History
# ------------------------------------------------
# Author        Date            Comments
# Loring        04/28/18        Ported from GoPiGo, converted to GoPiGo3
# Loring        09/06/21        Converted to Python3
# Loring        09/24/21        Refactored to OOP

############################################################################
# Includes the basic functions for controlling the GoPiGo Robot
import easygopigo3 as easy  # Import the GoPiGo library
import atexit               # Used for stopping the GoPiGo when closing the running program
import os                   # For placement of the pygame window
import sys                  # For sys.exit
import pygame               # Gives access to KEYUP/KEYDOWN events


class RemoteControlGUI:
    """ Remote control class  """

    def __init__(self):
        """ Initialize remote control class """
        self.gpg = easy.EasyGoPiGo3()

        # Set initial speed
        self.gpg.set_speed(200)

        # When the program exits, stop the GoPiGo
        # Unconfigure the sensors, disable the motors
        # and restore the LED to the control of the GoPiGo3 firmware
        atexit.register(self.gpg.reset_all)

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()

        # Constants for colors
        self.WHITE = (250, 250, 250)
        self.BLACK = (10, 10, 10)

        # Turn the blinkers off
        self.gpg.led_off("left")
        self.gpg.led_off("right")

        # Set window location
        X = 50
        Y = 50
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (X, Y)

        # Initialization for pygame
        pygame.init()
        # Set window size
        self.window = pygame.display.set_mode((425, 350))
        pygame.display.set_caption('GoPiGo Remote Control')

        # Create a surface object to draw on the same size as the screen
        background = pygame.Surface(self.window.get_size())
        # Convert the background surface to the same pixel display as the device
        self.background = background.convert()
        # Fill the background with black
        self.background.fill(self.BLACK)

# -------------------------- DISPLAY INSTRUCTIONS ------------------------ #
    def display_instructions(self):
        """ Create and display instructions for the GUI """
        # Create instructions for remote control of the robot
        instructions = '''                     GOPIGO REMOTE CONTROL

    (Put focus on this window to control the gopigo!)

        Press:
            W: Forward        L: Spin left
            A: Left                 O: Spin right
            D: Right
            S: Backward
            T: Increase speed    
            G: Decrease speed
            Z: Exit
        '''

        # Create font for display
        self.font = pygame.font.SysFont(None, 24)

        size_inc = 22   # Move down this many pixels for each line
        index = 0       # Counter for the loop

        # Print instructions on screen one line at a time
        for line in instructions.split('\n'):
            text = self.font.render(line, True, self.WHITE)
            self.background.blit(text, (10, 10+size_inc*index))
            index += 1

        # Create label to display speed
        label = self.font.render(
            'Speed: ' + str(self.gpg.get_speed()),   # String to display
            True,         # Turn on Anti Aliasing
            self.WHITE    # Color of text
        )
        # Blit everything to a screen buffer
        self.window.blit(
            self.background,  # Object to draw
            (0, 0)            # x, y coordinates
        )
        self.window.blit(
            label,            # Object to draw
            (10, 300)         # x, y coordinates
        )
        # Update the screen from the screen backbuffer
        pygame.display.update()

# ----------------------- INCREASE SPEED --------------------------------- #
    def increase_speed(self):
        """ Increase the speed of the GoPiGo """
        # Get the current speed
        speed = self.gpg.get_speed()
        # Add 100 to the current speed
        speed = speed + 100
        # Keep speed from going beyond 1000
        if (speed > 1000):
            speed = 1000
        # Set the new speed
        self.gpg.set_speed(speed)
        # Display speed
        lbl_speed = self.font.render(
            'Speed: ' + str(self.gpg.get_speed()), True, self.WHITE)
        # Blit everything to the screen backbuffer
        self.window.blit(
            self.background,  # What to draw
            (0, 0)            # x, y coordinates
        )
        self.window.blit(
            lbl_speed,        # Object to draw
            (10, 300)         # x, y coordinates
        )

# ------------------------- DECREASE SPEED -------------------------------- #
    def decrease_speed(self):
        """ Decrease the speed of the GoPiGo """
        # Get current speed
        speed = self.gpg.get_speed()
        # Subtract 100 from the current speed
        speed = speed - 100
        # Keep speed from going below 0
        if (speed < 0):
            speed = 0
        # Set the speed
        self.gpg.set_speed(speed)
        # Create label for speed display
        label = self.font.render(
            'Speed: ' + str(self.gpg.get_speed()), True, self. WHITE)
        # Blit everything to the backbuffer
        self.window.blit(self.background, (0, 0))
        self.window.blit(label, (10, 300))

# --------------------------- MENU LOOP ---------------------------------- #
    def menu_loop(self):
        """ Loop to capture keystrokes """
        while True:
            # Capture any events
            event = pygame.event.wait()
            # If the event is a keyup event
            # Stop everything
            if (event.type == pygame.KEYUP):
                self.gpg.stop()
                # Make sure the blinkers are off
                self.gpg.led_off("left")
                self.gpg.led_off("right")
                # Go to the next loop iteration
                continue
            # If the event is not a keydown
            # Go the next loop iteration
            if (event.type != pygame.KEYDOWN):
                continue

            # Get the keyboard character from the keydown event
            char = event.unicode

            # Move Forward
            if char == 'w':
                self.gpg.forward()

            # Turn Left
            elif char == 'a':
                self.gpg.left()
                self.gpg.led_on("left")

            # Turn Right
            elif char == 'd':
                self.gpg.right()
                self.gpg.led_on("right")

            # Move Backward
            elif char == 's':
                self.gpg.backward()
                # Turn both blinkers on
                self.gpg.led_on("left")
                self.gpg.led_on("right")

            # Spin Left
            elif char == 'l':
                self.gpg.spin_left()
                self.gpg.led_on("left")

            # Spin Right
            elif char == 'o':
                self.gpg.spin_right()
                self.gpg.led_on("right")

            # Increase Speed
            elif char == 't':
                self.increase_speed()

            # Decrease Speed
            elif char == 'g':
                self.decrease_speed()

            # Exit Program
            elif char == 'z':
                print("\nExiting")
                sys.exit()

            # Limit loop to 60 frames per second
            self.clock.tick(60)

            # Update the screen from the backbuffer
            pygame.display.update()


def main():
    # Create remote control object
    remote_control_gui = RemoteControlGUI()
    remote_control_gui.display_instructions()
    remote_control_gui.menu_loop()


# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()
