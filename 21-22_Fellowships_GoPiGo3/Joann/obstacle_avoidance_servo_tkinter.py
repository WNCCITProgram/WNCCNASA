# Import time and the GoPiGo3 library
import time
import easygopigo3 as easy
# Import the tkinter module with tk standard widgets
from tkinter import *
# Override tk widgets with themed ttk widgets if available
from tkinter.ttk import * 



class ObstacleAvoidanceGUI:

    def __init__(self):
        """
            Define the initialize method
        """
        # Create an instance of the GoPiGo3 class.
        # GPG will be the GoPiGo3 object.
        self.gpg = easy.EasyGoPiGo3()
        self.servo = gpg.init_servo("SERVO1")


        # Create an instance/object of the Distance Sensor class.
        # I2C1 and I2C2 are just labels used for identifying the port on the GoPiGo3 board.
        # But technically, I2C1 and I2C2 are the same thing, so we don't have to pass any port to the constructor.
        self.my_distance_sensor = gpg.init_distance_sensor()

        # Read the sensor into variables
        # mm = str(my_distance_sensor.read_mm())
        self.distanceInches = my_distance_sensor.read_inches()

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
        # Create the root window
       
    # Function to make the GoPiGo moving
    def obstacle_avoidance(self, *args):

        # Servo for a show purposes only
        # Right
        print("Right")
        servo.rotate_servo(150)
        time.sleep(1)

        # Left
        print("Left")
        servo.rotate_servo(10)
        time.sleep(1)

        # Forward
        print("Forward")
        servo.rotate_servo(90)
        time.sleep(1)

        # Drive forward
        gpg.forward()   

        # While true desicion to detect the obstacle
        while True:

            # Read the distance
            distanceInches = my_distance_sensor.read_inches()
            # Decision to detect the distance
            if distanceInches <= 10:
                print("You're too close!")
                gpg.stop()
                # Servo turn right
                servo.rotate_servo(150)
                time.sleep(1)
                # Read the sensor into a variable
                distR = my_distance_sensor.read_inches()
                # Rotate the servo to the left
                servo.rotate_servo(10)
                time.sleep(1)
                # Read the sensor into a variable
                distL = my_distance_sensor.read_inches()
                # Desicion which distance is longer
                if distR > distL:
                    # Rotate the servo forward before moving
                    servo.rotate_servo(90)
                    time.sleep(1)
                    # Turn GoPiGo to the right
                    gpg.turn_degrees(-90)
                    time.sleep(1)
                    # Move forward
                    gpg.forward()
                else:
                    # Rotate the servo forward before moving
                    servo.rotate_servo(90)
                    time.sleep(1)
                    # Turn GoPiGo to the left
                    gpg.turn_degrees(90)
                    time.sleep(1)
                    # Move forward
                    gpg.forward()


    # sleep is only needed to see the measurements
    # sleep is blocking code, nothing else can happen during sleep
    # Don't use in production code
    # time.sleep(1)
