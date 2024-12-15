"""
    Name: temperature_obstacle_avoidance.py
    Written by:
    Written on:
    Purpose:
"""
# Import time and the GoPiGo3 library
import time
import easygopigo3 as easy
# Import tkinter for GUI
from tkinter import * 
# Override tk widgets with themed ttk widgets if available
from tkinter.ttk import *
# Used to exit the program 
import sys
# EasyTHPSensor rounds data to 0 decimal for temp and humidity
from di_sensors.easy_temp_hum_press import EasyTHPSensor
#from easygopigo3 import EasyGoPiGo3


class ObstacleAvoidance:

    def __init__(self):
        ''' Initialize the program '''
        # Declare Variables
        self.distL = 0
        self.distR = 0
        self.distance_inches = 0
        # Detection distance in inches
        self.OBSTACLE_DISTANCE = 10
        # Initialize an EasyGoPiGo3 object
        self.gpg = easy.EasyGoPiGo3()
        self.servo = self.gpg.init_servo("SERVO1")
        # Set initial speed 
        self.gpg.set_speed(200)
        # Create an instance/object of the Distance Sensor class                     
        self.my_distance_sensor = self.gpg.init_distance_sensor()
        # Read the sensor into variables
        self.distance_inches = self.my_distance_sensor.read_inches()

        # Initialize an EasyTHPSensor object
        self.my_thp = EasyTHPSensor
        
        # Call the methods
        self.sensors_temp_hum_press()
        self.show_servo()
        self.move_forward()
        
        # While true desicion to detect the obstacle
        while True:
            try:
                
                self.detect_obstacle()
                
                
                
            # except the program gets interrupted by Ctrl+C on the keyboard.
            except KeyboardInterrupt:
                # Unconfigure the sensors, disable the motors, and
                # restore the LED to the control of the GoPiGo3 firmware.
                self.gpg.reset_all()
                exit(0)

            
    def show_servo(self):
        '''show_servo is for show purposes only'''
        # Right
        print("Right")
        self.servo.rotate_servo(150)
        time.sleep(1)

        # Left
        print("Left")
        self.servo.rotate_servo(10)
        time.sleep(1)

        # Forward
        print("Forward")
        self.servo.rotate_servo(90)
        time.sleep(1)

    def move_forward(self):
        # Drive forward
        self.gpg.forward()

    def detect_obstacle(self):
        # Read the distance
        self.distance_inches = self.my_distance_sensor.read_inches()
        # Desicion to detect the distance
        if self.distance_inches <= self.OBSTACLE_DISTANCE:
            print("You're too close!")
            self.gpg.stop()
            # Servo turn right
            self.servo.rotate_servo(150)
            time.sleep(1)
            # Read the sensor into a variable
            self.distR = self.my_distance_sensor.read_inches()
            # Rotate the servo to the left
            self.servo.rotate_servo(10)
            time.sleep(1)
            # Read the sensor into a variable
            self.distL = self.my_distance_sensor.read_inches()
            # Rotate the servo forward before moving
            self.servo.rotate_servo(90)
            time.sleep(1)
            self.avoid_obstacle()
    
    def avoid_obstacle(self):
        if self.distR > self.distL:

            self.gpg.turn_degrees(-90)
            time.sleep(1)
        else:
            self.gpg.turn_degrees(90)
            time.sleep(1)
        self.gpg.forward()

    def find_longer_distance(self):
       
        # Desicion which distance is longer
        if self.distR > self.distL:
            # Rotate the servo forward before moving
            self.servo.rotate_servo(90)
            time.sleep(1)
            # Turn GoPiGo to the right
            self.gpg.turn_degrees(-90)
            time.sleep(1)
            # Move forward
            self.gpg.forward()
        else:
            # Rotate the servo forward before moving
            self.servo.rotate_servo(90)
            time.sleep(1)
            # Turn GoPiGo to the left
            self.gpg.turn_degrees(90)
            time.sleep(1)
            # Move forward
            self.gpg.forward()

    def sensors_temp_hum_press(self):

        try:
            while True:
                # Read temperature
                # temp = my_thp.safe_celsius()
                temp = self.my_thp.safe_fahrenheit()

                # Read relative humidity
                hum = self.my_thp.safe_humidity()

                # Read pressure in pascals
                press = self.my_thp.safe_pressure()

                # Convert pascals to inHg, compensate for 4000' altitude
                press = (press / 3386.38867) + 4.08

                # Print values to the console
                print("Temp: {:5.1f} °F  Humidity: {:5.1f}%  Pressure: {:5.2f}".format(
                    temp, hum, press))

                # Pause between readings
                time.sleep(5)

        # Except the program gets interrupted by Ctrl+C on the keyboard.
        except KeyboardInterrupt:
            # Unconfigure the sensors, disable the motors,
            # and restore the LED to the control of the GoPiGo3 firmware
            self.gpg.reset_all()



# Create program object to run program
#temperature_obstacle_avoidance = ObstacleAvoidance()