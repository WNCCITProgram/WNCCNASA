#!/usr/bin/env python3
# Based on https://pythonprogramming.net/robotics-raspberry-pi-tutorial-gopigo-introduction
# EasyGoPiGo3 documentation: https://gopigo3.readthedocs.io/en/latest
# Purpose: GoPiGo3 Tkinter remote control program
# ------------------------------------------------
# History
# ------------------------------------------------
# Author     Date           Comments
# Loring     09/12/21       Convert to EasyGoPiGo3, OOP, test with Python 3.5
# Loring     10/23/21       Add battery voltage display
# Loring     11/23/21       Add ttk themed widgets and frames

from tkinter import *       # Import tkinter for GUI
from tkinter.ttk import *   # Add ttk themed widgets
import sys                  # Used to exit the program
import easygopigo3 as easy  # Import EasyGoPiGo3 library


class GoPiGoGUI:
    def __init__(self):
        """ Initialize the program """
        # Create EasyGoPiGo3 object
        self.gpg = easy.EasyGoPiGo3()
        self.gpg.set_speed(200)  # Set initial speed

        self.window = Tk()
        self.window.title("GoPiGo Remote Control")
        # Set the window size and location
        # 350x250 pixels in size, location at 50x50
        self.window.geometry("375x320+50+50")
        # Bind all key input events to the window
        # This will capture all keystrokes for remote control of robot
        self.window.bind_all('<Key>', self.key_input)
        # Create and layout widgets
        self.create_widgets()
        mainloop()      # Start the mainloop of the tkinter program

# -------------------------- CREATE WIDGETS ------------------------------ #
    def create_widgets(self):
        """ Create and layout widgets """
        # Reference for GUI display
        """
            W = Forward      Q = Spin Left
            S = Backward     E = Spin Right
            A = Left         T = Increase Speed
            D = Right        G = Decrease Speed  
            Spacebar = Stop
            Speed: 200      Voltage 
            Z = Exit    Exit button
        """
        # Create frames
        # Create main label frame to hold remote control widgets
        self.main_frame = LabelFrame(
            self.window,
            text="Remote Control",
            relief=GROOVE)
        # Create main frame to hold widgets
        self.bottom_frame = LabelFrame(
            self.window,
            relief=GROOVE)

        # Fill the frame to the width of the window
        self.main_frame.pack(fill=X, padx=10, pady=(10, 0))
        self.bottom_frame.pack(fill=X, padx=10, pady=10)
        # Keep the frame size regardless of the widget sizes
        self.main_frame.pack_propagate(False)
        self.bottom_frame.pack_propagate(False)

        # Create widgets and attach them to the correct frame
        lbl_remote_w = Label(self.main_frame, text="W: Forward")
        lbl_remote_q = Label(self.main_frame, text="Q: Spin Left")
        lbl_remote_s = Label(self.main_frame, text="S: Backward")
        lbl_remote_e = Label(self.main_frame, text="E: Spin Right")
        lbl_remote_a = Label(self.main_frame, text="A: Left")
        lbl_remote_d = Label(self.main_frame, text="D: Right")
        lbl_remote_t = Label(self.main_frame, text="T: Increase Speed")
        lbl_remote_g = Label(self.main_frame, text="G: Decrease Speed")
        lbl_remote_spacebar = Label(self.main_frame, text="Spacebar: Stop")
        lbl_remote_z = Label(self.bottom_frame, text="Z: Exit")

        # Get and display battery voltage
        btn_voltage = Button(
            self.bottom_frame,
            text="Voltage",
            command=self.get_battery_voltage)

        # Round the voltage to 1 decimal place
        voltage = round(self.gpg.volt(), 1)
        self.lbl_voltage = Label(
            self.bottom_frame,
            text="Voltage: " + str(voltage) + "V")

        btn_exit = Button(
            self.bottom_frame,
            text="Exit",
            command=self.exit_program)

        # Get and display current GoPiGo speed setting
        speed = self.gpg.get_speed()
        self.lbl_speed = Label(self.bottom_frame, text="Speed: " + str(speed))

        # Grid the widgets
        lbl_remote_w.grid(row=0, column=0, sticky=W)
        lbl_remote_q.grid(row=0, column=1, sticky=W)
        lbl_remote_s.grid(row=1, column=0, sticky=W)
        lbl_remote_e.grid(row=1, column=1, sticky=W)
        lbl_remote_a.grid(row=2, column=0, sticky=W)
        lbl_remote_t.grid(row=2, column=1, sticky=W)
        lbl_remote_d.grid(row=3, column=0, sticky=W)
        lbl_remote_g.grid(row=3, column=1, sticky=W)
        lbl_remote_spacebar.grid(row=4, column=0, sticky=W)

        self.lbl_speed.grid(row=0, column=0, sticky=W)
        btn_voltage.grid(row=0, column=1, sticky=E)
        self.lbl_voltage.grid(row=0, column=2, sticky=W)
        lbl_remote_z.grid(row=1, column=0, sticky=W)
        btn_exit.grid(row=1, column=1, sticky=E)

        # Set padding for all widgets in frames
        pad = 6
        for child in self.main_frame.winfo_children():
            child.grid_configure(padx=pad, pady=pad)
        for child in self.bottom_frame.winfo_children():
            child.grid_configure(padx=pad, pady=pad)

# ------------------------- INCREASE SPEED ------------------------------- #
    def increase_speed(self):
        """ Increase the speed of the GoPiGo """
        speed = self.gpg.get_speed()    # Get the current speed
        speed = speed + 100             # Add 100 to the current speed
        # Keep speed from going beyond 1000
        if (speed > 1000):
            speed = 1000
        self.gpg.set_speed(speed)       # Set the new speed
        # Display current speed
        self.lbl_speed.config(text="Speed: " + str(speed))

# -------------------------- DECREASE SPEED ------------------------------ #
    def decrease_speed(self):
        """ Decrease the speed of the GoPiGo """
        speed = self.gpg.get_speed()    # Get current speed
        speed = speed - 100             # Subtract 100 from the current speed
        # Keep speed from going below 0
        if (speed < 100):
            speed = 100
        self.gpg.set_speed(speed)       # Set the new speed
        # Display current speed
        self.lbl_speed.config(text="Speed: " + str(speed))

# ------------------------ GET BATTERY VOLTAGE --------------------------- #
    def get_battery_voltage(self):
        voltage = round(self.gpg.volt(), 1)
        self.lbl_voltage.config(text="Voltage: " + str(voltage) + "V")

# -------------------------- EXIT PROGRAM -------------------------------- #
    def exit_program(self):
        """ Exit the program """
        self.window.destroy()

# --------------------------- KEY INPUT ---------------------------------- #
    def key_input(self, event):
        # Get all key preseses as lower case
        key_press = event.keysym.lower()
        # print(key_press)  # For testing

        # Move Forward
        if key_press == 'w':
            self.gpg.forward()

        # Move Backward
        elif key_press == 's':
            self.gpg.backward()
            # Turn both blinkers on
            self.gpg.led_on("left")
            self.gpg.led_on("right")

        # Turn Left
        elif key_press == 'a':
            self.gpg.left()
            self.gpg.led_on("left")

        # Turn Right
        elif key_press == 'd':
            self.gpg.right()
            self.gpg.led_on("right")

        # Spin Left
        elif key_press == 'q':
            self.gpg.spin_left()
            self.gpg.led_on("left")

        # Spin Right
        elif key_press == 'e':
            self.gpg.spin_right()
            self.gpg.led_on("right")

        # Increase Speed
        elif key_press == 't':
            self.increase_speed()

        # Decrease Speed
        elif key_press == 'g':
            self.decrease_speed()

        # Stop
        elif key_press == 'space':
            self.gpg.stop()
            # Turn off the blinkers
            self.gpg.led_off("left")
            self.gpg.led_off("right")

        # Exit program
        elif key_press == 'z':
            self.exit_program()


# Create remote control object
gopigo_gui = GoPiGoGUI()
