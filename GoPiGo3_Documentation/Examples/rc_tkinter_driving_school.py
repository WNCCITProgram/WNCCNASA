#!/usr/bin/env python3
"""
    Name:    rc_tkinter_driving_school.py
    Author:  William A Loring
    Created: 12/04/2021
    Purpose: GoPiGo Tkinter based driving school program
"""

# ------------------------------------------------
# History
# ------------------------------------------------
# Author     Date           Comments


from tkinter import *       # Import tkinter for GUI
from tkinter.ttk import *   # Add ttk themed widgets
import sys                  # Used to as sys.exit() to exit the program
import easygopigo3 as easy  # Import EasyGoPiGo3 library


class GoPiGoGUI:
    def __init__(self):
        """ Initialize the program """
        self.gpg = easy.EasyGoPiGo3()  # Create EasyGoPiGo3 object
        self.gpg.set_speed(200)        # Set initial speed
        self.window = Tk()             # Create Tkinter window
        self.window.title("GoPiGo Driving School")
        # Set the window size and location
        # 375x320 pixels in size, location at 50x50
        self.window.geometry("375x320+50+50")
        self.create_widgets()  # Create and layout widgets
        mainloop()             # Start Tkinter program main loop

# --------------------------- CREATE WIDGETS ------------------------------#
    def create_widgets(self):
        """ Create and layout widgets """
        # Create main label frame to hold remote control widgets
        self.main_frame = LabelFrame(
            self.window,
            text="Driving School",
            relief=GROOVE)

        # Pack the frame to the width (X) of the window
        self.main_frame.pack(fill=X, padx=10, pady=(10))
        # Keep the frame size regardless of the widget sizes
        self.main_frame.pack_propagate(False)

        # Create widgets and attach them to the correct frame
        btn_square = Button(
            self.main_frame,
            text="Square Right",
            command=self.square_right)

        btn_exit = Button(
            self.main_frame,
            text="Exit",
            command=self.exit_program)

        # Grid the widgets
        btn_square.grid(row=0, column=0,)
        btn_exit.grid(row=0, column=1)

        # Set padding between frame and window
        self.main_frame.pack_configure(padx=10, pady=(10))
        # Set padding for all widgets in frames
        pad = 10
        for child in self.main_frame.winfo_children():
            child.grid_configure(padx=pad, pady=pad)

# ------------------------- DRIVE RIGHT SQUARE ----------------------------#
    def square_right(self):
        for i in range(4):
            self.gpg.drive_inches(12)
            self.gpg.turn_degrees(90)

# ----------------------------- EXIT PROGRAM ------------------------------#
    def exit_program(self):
        # Unconfigure the sensors, disable the motors,
        # restore the LED to the control of the GoPiGo3 firmware
        self.gpg.reset_all()
        sys.exit()


# Create program object
gopigo_gui = GoPiGoGUI()
