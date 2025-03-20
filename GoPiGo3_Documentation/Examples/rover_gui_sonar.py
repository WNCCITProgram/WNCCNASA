#!/usr/bin/env python3
"""
    Name: rover_gui_sonar.py
    Author: William A Loring
    Created: 12/18/21
    Purpose: Python tkinter program to 
    control MARS rover and use ultrasonic sensor
"""
# ------------------------------------------------
# History
# ------------------------------------------------
# Author     Date           Comments
# Loring


from tkinter import *       # Import tkinter for GUI
from tkinter.ttk import *   # Add ttk themed widgets
import rover                # Import MARS Rover library
# Read the number of LED's
NUM_LEDS = rover.numPixels
# Set RGB color constants
RED = rover.fromRGB(127, 0, 0)
ORANGE = rover.fromRGB(127, 127, 0)
GREEN = rover.fromRGB(0, 127, 0)
BLUE = rover.fromRGB(0, 0, 127)
BLACK = rover.fromRGB(0, 0, 0)
WHITE = rover.fromRGB(127, 127, 127)

# LED Pin mapping
LF_LED = 1
RF_LED = 2
LR_LED = 0
RR_LED = 3

# Initialize the rover library and LED's
rover.init(40)

# Turn off all LED's
for i in range(NUM_LEDS):
    rover.setPixel(i, BLACK)
    rover.show()


class RoverGUI:
    def __init__(self):
        """ Initialize the program """
        # Set servo physical pin numbers
        self.servo_FL = 9
        self.servo_RL = 11
        self.servo_FR = 15
        self.servo_RR = 13
        self.servo_MA = 0

        # Set initial speed
        self.speed = 50

        # Create window
        self.window = Tk()
        self.window.title("MARS Rover Remote")

        # Set the window size and location
        # 350x250 pixels in size, location at 50x50
        self.window.geometry("300x350+50+50")

        # Bind all key input events to the window
        # This will capture all keystrokes for remote control of robot
        self.window.bind_all('<Key>', self.key_input)

        # Create and layout widgets
        self.create_widgets()
        mainloop()

# ------------------------------ START SONAR ------------------------------#
    def start_sonar(self):
        # Get distance in centimeters
        self.btn_start_sonar["state"] = "disabled"
        self.btn_stop_sonar["state"] = "enabled"
        # Get distance in cm
        dist_cm = rover.getDistance()
        # Convert cm to inches
        dist_inches = round(dist_cm * .393701)

        # Convert inches to feet and inches
        # Use integer division and modulus
        dist_feet = dist_inches // 12
        dist_inches = dist_inches % 12
        # Display distance on label
        self.lbl_sonar_distance.configure(
            text=f'{dist_feet} ft {dist_inches}\"')
        # Take a reading every 250 ms when main program thread isn't busy
        self.sonar_id = self.window.after(250, self.start_sonar)

# ------------------------------ STOP SONAR -------------------------------#
    def stop_sonar(self):
        if self.sonar_id:
            self.window.after_cancel(self.sonar_id)
            self.sonar_id = None
        self.btn_start_sonar["state"] = "enabled"
        self.btn_stop_sonar["state"] = "disabled"
        self.lbl_sonar_distance.configure(text='')

# --------------------------------- FORWARD -------------------------------#
    def go_forward(self):
        self.reset_leds()
        rover.setPixel(LF_LED, GREEN)
        rover.setPixel(RF_LED, GREEN)
        rover.show()
        self.reset_servos()
        rover.forward(self.speed)

# --------------------------------- REVERSE -------------------------------#
    def go_reverse(self):
        self.reset_leds()
        rover.setPixel(LR_LED, GREEN)
        rover.setPixel(RR_LED, GREEN)
        rover.show()
        self.reset_servos()
        rover.reverse(self.speed)

# -------------------------- LEFT -----------------------------------------#
    def go_left(self):
        self.reset_leds()
        rover.setPixel(LF_LED, GREEN)
        rover.show()
        rover.setServo(self.servo_FL, -20)
        rover.setServo(self.servo_FR, -20)
        rover.setServo(self.servo_RL, 20)
        rover.setServo(self.servo_RR, 20)

# -------------------------- RIGHT ----------------------------------------#
    def go_right(self):
        self.reset_leds()
        rover.setPixel(RF_LED, GREEN)
        rover.show()
        rover.setServo(self.servo_FL, 20)
        rover.setServo(self.servo_FR, 20)
        rover.setServo(self.servo_RL, -20)
        rover.setServo(self.servo_RR, -20)

# ------------------------- RESET SERVOS ----------------------------------#
    def reset_servos(self):
        """Set all wheel steering servos to 0 (straight ahead)"""
        rover.setServo(self.servo_FL, 0)
        rover.setServo(self.servo_FR, 0)
        rover.setServo(self.servo_RL, 0)
        rover.setServo(self.servo_RR, 0)

# --------------------------------- RESET LEDS ----------------------------#
    def reset_leds(self):
        rover.setPixel(LF_LED, BLACK)
        rover.setPixel(RF_LED, BLACK)
        rover.setPixel(LR_LED, BLACK)
        rover.setPixel(RR_LED, BLACK)
        rover.show()

# --------------------------------- INCREASE SPEED ------------------------#
    def increase_speed(self):
        """Increase current speed by 10, max 100"""
        self.speed = min(100, self.speed+10)
        self.lbl_speed.config(text=f"Speed: {self.speed}")

# --------------------------------- DECREASE SPEED ------------------------#
    def decrease_speed(self):
        """Decrease current speed by 10, min 0"""
        self.speed = max(0, self.speed-10)
        self.lbl_speed.config(text=f"Speed: {self.speed}")

# ----------------------------- EXIT PROGRAM ------------------------------#
    def exit_program(self):
        print("\nExiting")
        # Cleanup rover resources
        rover.cleanup()
        # Destroy the program object
        self.window.destroy()

# --------------------------------- KEY INPUT -----------------------------#
    def key_input(self, event):
        # Get all key presses as lower case
        key_press = event.keysym.lower()
        # print(key_press)  # For testing

        # Move Forward
        if key_press == 'w':
            self.go_forward()

        # Move Backward
        elif key_press == 's':
            self.go_reverse()

        # Turn Left
        elif key_press == 'a':
            self.go_left()

        # Turn Right
        elif key_press == 'd':
            self.go_right()

        # Increase Speed
        elif key_press == 't':
            self.increase_speed()

        # Decrease Speed
        elif key_press == 'g':
            self.decrease_speed()

        # Stop
        elif key_press == 'space':
            self.reset_leds()
            self.reset_servos()
            rover.stop()

        # Exit program
        elif key_press == 'z':
            self.exit_program()

# --------------------------------- CREATE WIDGETS ------------------------#
    def create_widgets(self):
        """ Create and layout widgets """
        # Reference for GUI display
        """
                    W = Forward
            S = Backward    A = Left
                    D = Right  
            T = Increase Speed  G = Decrease Speed  
            Spacebar = Stop
            Speed: 200
            Z = Exit    Exit button
        """
        # Create frames
        # Create main label frame to hold remote control widgets
        self.main_frame = LabelFrame(
            self.window,
            text="Remote Control",
            relief=GROOVE)
        self.middle_frame = LabelFrame(
            self.window,
            text="Speed",
            relief=GROOVE)

        self.bottom_frame = LabelFrame(
            self.window,
            text="Control",
            relief=GROOVE)

        # Fill the frame to the width of the window
        self.main_frame.pack(fill=X, padx=10, pady=(10, 10))
        self.middle_frame.pack(fill=X, padx=10, pady=(0))
        self.bottom_frame.pack(fill=X, padx=10, pady=10)

        # Keep the frame size regardless of the widget sizes
        self.main_frame.pack_propagate(False)
        self.middle_frame.pack_propagate(False)
        self.bottom_frame.pack_propagate(False)

        # Create widgets and attach them to the correct frame
        lbl_w_forward = Label(
            self.main_frame, text=" W: Forward", relief=RIDGE)
        lbl_s_reverse = Label(
            self.main_frame, text=" S: Reverse", relief=RIDGE)
        lbl_a_left = Label(self.main_frame, text=" A: Left", relief=RIDGE)
        lbl_d_right = Label(self.main_frame, text=" D: Right", relief=RIDGE)

        # Get and display current speed setting
        self.lbl_speed = Label(
            self.middle_frame, text=f"Speed: {self.speed}")

        lbl_t_increase_speed = Label(
            self.middle_frame, text="T: Increase Speed")
        lbl_g_decrease_speed = Label(
            self.middle_frame, text="G: Decrease Speed")
        lbl_spacebar_stop = Label(self.middle_frame, text="Spacebar: Stop")

        lbl_remote_z = Label(self.bottom_frame, text="Z: Exit")

        self.lbl_sonar_distance = Label(self.bottom_frame)
        self.btn_start_sonar = Button(
            self.bottom_frame,
            text="Start Sonar",
            command=self.start_sonar)
        self.btn_stop_sonar = Button(
            self.bottom_frame,
            text="Stop Sonar",
            command=self.stop_sonar)
        btn_exit = Button(
            self.bottom_frame,
            text="Exit",
            command=self.exit_program)

        # Grid the widgets
        lbl_w_forward.grid(row=0, column=1)
        lbl_a_left.grid(row=1, column=0)
        lbl_d_right.grid(row=1, column=2)
        lbl_s_reverse.grid(row=2, column=1)

        self.lbl_speed.grid(row=0, column=0, sticky=W)
        lbl_t_increase_speed.grid(row=1, column=0, sticky=W)
        lbl_g_decrease_speed.grid(row=1, column=1, sticky=W)
        lbl_spacebar_stop.grid(row=0, column=1, sticky=W)

        self.btn_start_sonar.grid(row=0, column=0)
        self.btn_stop_sonar.grid(row=0, column=1)
        self.lbl_sonar_distance.grid(row=0, column=3)

        lbl_remote_z.grid(row=1, column=0, sticky=W)
        btn_exit.grid(row=1, column=1, sticky=E)

        # Set padding for all widgets in frames
        pad = 6
        for child in self.main_frame.winfo_children():
            child.grid_configure(padx=3, pady=3, ipadx=2, ipady=2)
        for child in self.middle_frame.winfo_children():
            child.grid_configure(padx=pad, pady=pad)
        for child in self.bottom_frame.winfo_children():
            child.grid_configure(padx=pad, pady=pad)


# Create remote control object
rover_gui = RoverGUI()
