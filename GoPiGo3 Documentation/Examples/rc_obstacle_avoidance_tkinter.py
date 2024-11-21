#!/usr/bin/env python3

# Based on
# https://pythonprogramming.net/robotics-raspberry-pi-tutorial-gopigo-introduction
#
# This uses the EasyGoPiGo3 library
# https://gopigo3.readthedocs.io/en/master/api-basic/easygopigo3.html
#
# History
# ------------------------------------------------
# Author     Date           Comments
# Loring     09/12/21       Convert to EasyGoPiGo3, test with Python 3.5
# Loring     10/16/21       Add obstacle avoidance using after

from tkinter import *       # Import tkinter for GUI
import sys                  # Used to exit the program
import easygopigo3 as easy  # Import EasyGoPiGo3 library


class GoPiGoGUI:
    def __init__(self):
        """ Initialize the program """
        self.DETECTION_DISTANCE = 12   # Detection distance in inches
        self.gpg = easy.EasyGoPiGo3()  # Initialize an EasyGoPiGo3 object
        self.gpg.set_speed(200)        # Set initial speed

        # Initialize a distance sensor object
        self.distance_sensor = self.gpg.init_distance_sensor()

        # Initialize a servo object on Servo Port 2
        self.servo = self.gpg.init_servo("SERVO2")
        # Set servo pointing stright ahead
        self.servo.rotate_servo(90)

        self.window = Tk()  # Initialize a tkinter window object
        self.window.title("GoPiGo Remote Control")
        # Set the window size and location
        # 320x200 pixels in size, location at 100x100
        self.window.geometry("350x200+100+100")

        # Bind all key input events to the window
        # This will capture all keystrokes for remote control of robot
        self.window.bind_all('<Key>', self.key_input)

        self.create_widgets()       # Create and layout widgets

        # after runs a function so many milliseconds after the mainloop starts
        # this callback function runs when the mainloop isn't busy
        # after is a non blocking call, it does not interrupt or stall execution
        self.window.after(1000, self.obstacle_detection)

        self.window.mainloop()      # Start the mainloop of the tkinter program

# --------------------- OBSTACLE DETECTION ------------------------------- #
    def obstacle_detection(self):
        """Obstacle detection routine, called every 100 ms from after method"""
        # Find the distance of the object in front
        dist = self.distance_sensor.read_inches()
        # Print feedback to the console for testing
        # print("Dist:", dist, 'inches')
        # If the object is closer than detection distance,
        # call the obstacle avoidance function
        if dist < self.DETECTION_DISTANCE:
            self.obstacle_avoidance()

        # A recursive call every 100 ms to read the sensor and decide what to do
        # after is a non blocking call, it runs the callback function when the main thread isn't busy
        self.window.after(1000, self.obstacle_detection)

# ------------------------- OBSTACLE AVOIDANCE --------------------------- #
    def obstacle_avoidance(self):
        """
            Obstacle avoidance routine
        """
        # Place any obstacle avoidance code here
        # This code is a proof of concept and a placeholder for your code
        # print("Stopping")    # Print feedback to the console
        self.gpg.turn_degrees(-90)
        self.gpg.forward()

# ------------------------ CREATE WIDGETS -------------------------------- #
    def create_widgets(self):
        """ Create and layout widgets """
        # Reference for GUI display
        """
        W = Forward      Q = Spin Left
        S = Backward     E = Spin Right
        A = Left         
        D = Right        Spacebar = Stop
        T = Increase Speed
        G = Decrease Speed
        Speed: 300
        """
        # Create widgets
        lbl_remote_w = Label(text="W: Forward")
        lbl_remote_q = Label(text="Q: Spin Left")
        lbl_remote_s = Label(text="S: Backward")
        lbl_remote_e = Label(text="E: Spin Right")
        lbl_remote_a = Label(text="A: Left")
        lbl_remote_spacebar = Label(text="Spacebar: Stop")
        lbl_remote_d = Label(text="D: Right")
        lbl_remote_t = Label(text="T: Increase Speed")
        lbl_remote_g = Label(text="G: Decrease Speed")
        lbl_remote_z = Label(text="Z: Exit")

        # Get and display current GoPiGo speed setting
        speed = self.gpg.get_speed()
        self.lbl_speed = Label(text="Speed: " + str(speed))

        # Grid the widgets
        lbl_remote_w.grid(row=0, column=0, sticky=W)
        lbl_remote_q.grid(row=0, column=1, sticky=W)
        lbl_remote_s.grid(row=1, column=0, sticky=W)
        lbl_remote_e.grid(row=1, column=1, sticky=W)
        lbl_remote_a.grid(row=2, column=0, sticky=W)
        lbl_remote_spacebar.grid(row=2, column=1, sticky=W)
        lbl_remote_d.grid(row=3, column=0, sticky=W)
        lbl_remote_t.grid(row=4, column=0, sticky=W)
        lbl_remote_g.grid(row=5, column=0, sticky=W)
        self.lbl_speed.grid(row=6, column=0, sticky=W)
        lbl_remote_z.grid(row=6, column=1, sticky=W)

        # Set padding for all widgets
        for child in self.window.winfo_children():
            child.grid_configure(padx=4, pady=4)

# ------------------------- INCREASE SPEED ------------------------------- #
    def increase_speed(self):
        """Increase the speed of the GoPiGo"""
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
        """Decrease the speed of the GoPiGo"""
        speed = self.gpg.get_speed()    # Get current speed
        speed = speed - 100             # Subtract 100 from the current speed
        # Keep speed from going below 0
        if (speed < 0):
            speed = 0
        self.gpg.set_speed(speed)       # Set the new speed
        # Display current speed
        self.lbl_speed.config(text="Speed: " + str(speed))

# --------------------------- KEY INPUT ---------------------------------- #
    def key_input(self, event):
        """Capture all keystroke events"""
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
            print("\nExiting")
            sys.exit()


# Create tkinter remote control object
gopigo_gui = GoPiGoGUI()
