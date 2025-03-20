"""
    Name: sons_of_driving_school_tkinter.py
    Author:
    Created: 10-19-2021
    Purpose: 
"""
# Import the time library for the sleep function
import time
# Import GoPiGo3 library
from easygopigo3 import EasyGoPiGo3
# Override tk widgets with themed ttk widgets if available
from tkinter.ttk import *
# Used to exit the program 
import sys 
# Import EasyGoPiGo3 library
import easygopigo3 as easy





#-------------------------Stage 1--------------------------------#
# Square
def square(self, *args):

    # Drive a right square based on the distance argument
    # Loop four times, Loop starts at 0,
    # Ends at 1 less than the last number
    # The loop increments 0, 1, 2, 3
    print("Make a square")
    for x in range(0, 4):
        # Print the loop counter
        #print(x)
        self.gpg.led_off("right")
        self.gpg.drive_inches(
            self.distance,       # How far to drive in inches
            True            # Blocking, nothing else can happen while moving
        )
        self.gpg.led_on("right")
        # Turn right 90 degrees, positive number is right
        self.gpg.turn_degrees(90)
    # Turn both blinkers off
    self.gpg.led_off("right")
    self.gpg.led_off("left")


# Rectangle
def rectangle(self, *args):
    # Drive a right rectangle based on the distance argument
    # Loop two times, Loop starts at 0,
    # Ends at 1 less than the last number
    # The loop increments 0, 1
    print("Make a rectangle")
    for x in range(0, 2):
        # Print the loop counter
        #print(x)
        self.gpg.led_off("right")
        self.gpg.drive_inches(
            self.distance1,       # How far to drive in inches
            True            # Blocking, nothing else can happen while moving
        )
        self.gpg.led_on("right")
        # Turn right 90 degrees, positive number is right
        self.gpg.turn_degrees(90)

        self.gpg.led_off("right")
        self.gpg.drive_inches(
            self.distance2,       # How far to drive in inches
            True            # Blocking, nothing else can happen while moving
        )
        self.gpg.led_on("right")
        # Turn right 90 degrees, positive number is right
        self.gpg.turn_degrees(90)

    # Turn both blinkers off
    self.gpg.led_off("right")
    self.gpg.led_off("left")

# Sentry
def sentry(self, *args):
    # Drive a right square based on the distance argument
    # Loop four times, Loop starts at 0,
    # Ends at 1 less than the last number
    # The loop increments 0, 1, 2, 3
    print("Make a Sentry")
    self.square(12)
    self.gpg.turn_degrees(90)
    for x in range(0, 4):
        # Print the loop counter
        #print(x)
        self.gpg.led_off("right")
        self.gpg.drive_inches(
            self.distance,       # How far to drive in inches
            True            # Blocking, nothing else can happen while moving
        )
        self.gpg.led_on("right")
        # Turn right 90 degrees, positive number is right
        self.gpg.turn_degrees(-90)

# Retrace
def retrace(self, *args):
    # Drive a right square based on the distance argument
    # Loop four times, Loop starts at 0,
    # Ends at 1 less than the last number
    # The loop increments 0, 1, 2, 3
    print("Make a Retrace")
    self.square(12)
    self.gpg.turn_degrees(-90)
    for x in range(0, 4):
        # Print the loop counter
        #print(x)
        self.gpg.led_off("right")
        self.gpg.drive_inches(
            self.distance,       # How far to drive in inches (has negative distance)
            True            # Blocking, nothing else can happen while moving
        )
        self.gpg.led_on("right")
        # Turn right 90 degrees, positive number is right
        self.gpg.turn_degrees(-90)

# ForwardReverse
def forwardReverse(self, *args):
    # Drive forward then turn 180 degrees, move backwards
    # Loop two times, Loop starts at 0
    # Ends at 1 less than the last number
    # The loop increments 0, 1
    print("Make a Forward Reverse")
    for x in range(0, 2):
        # Print the loop counter
        #print(x)
        self.gpg.drive_inches(self.distance, True)
        self.turn_degrees(180)
        self.drive_inches(self.distance, True)
        self.turn_degrees(180)

#--------------------------------Stage 2------------------------------------

# Octagon
def octagon(self, *args):
    # Drive 12" octagon
    # Starts and end at the same place and orientation
    # Each turn is a 45 degrees angle
    # Loop eight times, loop starts at 0
    # The loop increments 0, 1, 2, 3, 4, 5, 6, 7
    print("Make an Octagon")
    for x in range(0, 8):
        # Print the loop counter
        #print(x)
        self.gpg.drive_inches(self.distance, True)
        self.gpg.turn_degrees(45)

# Equilateral Triangle
def equilateralTriangle(self, *args):
    # Drive 12" equilateral triangle
    # Start and end in the same place and orientation
    print("Make an Equilateral Triangle")
    for x in range(0,3):
        # Print the loop counter
        #print(x)
        self.gpg.drive_inches(self.distance, True)
        self.gpg.turn_degrees(120)

# 5-Point Star
def fivePointStar(self, *args):
    # Drive to trace a 5-point 12"star
    # Start and end at the same location and orientation.
    print("Make a 5-Point Star")
    for x in range(0, 6): 
        self.gpg.drvie_inches(self.distance, True)
        self.gpg.turn_degrees(72)
        self.gpg.drvie_inches(self.distance, True)
        self.gpg.turn_degrees(144)

# If a standalone program, call the main function
# Else, use as a module
#if __name__ == '__main__':
    #main()
    
    # def create_widgets(self):
    #     """ Create and grid widgets """
    #     """
    #         1 = Square          5 = Forward Reverse
    #         2 = Rectangle       6 = Octagon
    #         3 = Sentry          7 = Equilateral Triangle
    #         4 = Retrace         8 = Five Point Star
    #     """
    #     # Create main label frame to hold widgets
    #     self.main_frame = LabelFrame(
    #         self.window,
    #         text="Enter Polygon Sides",
    #         relief=GROOVE)
        
    #     # Create entry widget in the frame to get input from user
    #     self.btn1_calculate = Button(
    #         self.main_frame,
    #         text='Square',
    #         command=self.square)

    #     # Create entry widget in the frame to get input from user
    #     self.btn2_calculate = Button(
    #         self.main_frame,
    #         text='Rectangle',
    #         command=self.rectangle)

    #     # Create entry widget in the frame to get input from user
    #     self.btn3_calculate = Button(
    #         self.main_frame,
    #         text='Sentry',
    #         command=self.sentry)

    #     # Create entry widget in the frame to get input from user
    #     self.btn4_calculate = Button(
    #         self.main_frame,
    #         text='Retrace',
    #         command=self.retrace)

    #     # Create entry widget in the frame to get input from user
    #     self.btn5_calculate = Button(
    #         self.main_frame,
    #         text='Forward Reverse',
    #         command=self.forwardReverse)

    #     # Create entry widget in the frame to get input from user
    #     self.btn6_calculate = Button(
    #         self.main_frame,
    #         text='Octagon',
    #         command=self.octagon)

    #     # Create entry widget in the frame to get input from user
    #     self.btn7_calculate = Button(
    #         self.main_frame,
    #         text='Equilateral Triangle',
    #         command=self.equilateralTriangle)

    #     # Create entry widget in the frame to get input from user
    #     self.btn8_calculate = Button(
    #         self.main_frame,
    #         text='Five Point Star',
    #         command=self.fivePointStar)

    #     # Use Grid layout manager to place widgets in the frame
    #     self.btn1_calculate.grid(row=0, column=0)
    #     self.btn2_calculate.grid(row=1, column=0)
    #     self.btn3_calculate.grid(row=2, column=0)
    #     self.btn4_calculate.grid(row=3, column=0)
    #     self.btn5_calculate.grid(row=0, column=1)
    #     self.btn6_calculate.grid(row=1, column=1)
    #     self.btn7_calculate.grid(row=2, column=1)
    #     self.btn8_calculate.grid(row=3, column=1)

    #     # Set padding between frame and window
    #     self.main_frame.grid_configure(padx=10, pady=10)
    #     # Set padding for all widgets inside the frame
    #     for widget in self.main_frame.winfo_children():
    #         widget.grid_configure(padx=5, pady=5)

        


# Create remote control object
#gopigo_gui = SonsOfDrivingSchoolGUI()

