# name: driving_school.py


#--------------------------------- IMPORTS -------------------------------------#
import time                                   # Import time library for sleep function
import easygopigo3 as easy 
from tkinter import * 
import tkinter as tk
                   # Import the GoPiGo3 library
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
#Print menu 
#menu method 
    while True:
        print_menu_choice()
        menu_choice = int(input("Please pick a number from the menu: "))
        if(menu_choice ==1):
            right_square_turn()
        elif(menu_choice ==2):
            left_square_turn()
        elif(menu_choice == 3):
            triangle_turn()
        elif(menu_choice == 4):
            octagon_turn()
        elif(menu_choice ==5):
            five_point_star()

def print_menu_choice():
    print("1. right square turn:")
    print("2. left square turn: ")
    print("3. triangle turn: ")
    print("4. octagon turn: ")
    print("5. 5 point star turn: ")


def right_square_turn(): # Menu option 1
    # need a way to start it I think
    for x in range(4):
        gpg.drive_inches(12)
        gpg.turn_degrees(90)

def left_square_turn(): #Menu option 2
    for x in range(4): # loop the things so I don't have to type that shit 4 times 
        gpg.drive_inches(12) #go forward 12 inches
        gpg.turn_degrees(-90) #-90 degrees is turning left I think

def triangle_turn(): # Menu option 3
    for x in range(3):
        gpg.drive_inches(12) #go forward 12 inches
        gpg.turn_degrees(120) # 60 degrees is interior angle for a triangle. If this gives weird results, try the anterior angle of 120


def octagon_turn(): #Option 4
    for x in range(8): #Loop it 8 times to complete the shape
        gpg.drive_inches(12) #forward 12inches
        gpg.turn_degrees(45) #45 degrees for each turn

def five_point_star():#Option 5 #stars have like a lot of angles. 
    for x in range (5):
        gpg.drive_inches(12) #12 inches
        gpg.turn_degrees(252) #idk if that is right maybe 72, or 108

def obstacle_avoid():
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


def create_widgets(self):
        """
        create and grid widgets
        """

        # Create a main label frame to hold widgets
        self.main_frame = LabelFrame(
            self.window,
            bg='#c6ff9e',
            text="Click a button",
            relief=GROOVE)

         # Create entry widget in the frame to get input from the user
        self.enter_sides = Entry(
            self.main_frame,
            text='',
            bg="#9eebff",
            width=30)
        
        # Create button in the frame to call calculate method
        self.btn_right_square = Button(
            self.main_frame,
            text='RIght Square Turn',
            bg='green',
            fg='light yellow',
            width=20,
            command=self.right_square_turn)

        

        # Create a second label frame to hold widgets
        self.sub_frame = LabelFrame(
            self.window,
            bg='#c6ff9e',
            text="Enter Length of a Side in Inches",
            relief=GROOVE)
    
        # Create entry widget in the frame to get input for the inches of the sides from the user
        self.enter_inches = Entry(
            self.sub_frame,
            text='',
            bg="#9eebff",
            width=30)
                  
        # Create button in the frame to call calculate method
        self.btn_calculate_perimeter = Button(
            self.sub_frame,
            text='Calculate Perimeter',
            bg='green',
            fg='light yellow',
            width=20,
            command=self.calculate_perimeter)


        self.third_frame = LabelFrame(
            self.window,
            bg='#c6ff9e',
            text="Display",
            relief=GROOVE)
        # Create label in the frame to show interior angle
        self.lbl_interior = Label(
            self.third_frame,
            width=25,
            bg="#b39eff",
            relief=GROOVE)

        # Create label in the frame to show exterior angle
        self.lbl_exterior = Label(
            self.third_frame,
            width=25,
            bg="#b39eff",
            relief=GROOVE)

        # Create label in the frame to show permeter
        self.lbl_perimeter = Label(
            self.third_frame,
            bg="#b39eff",
            width=25,
            relief=GROOVE)

        # Use grid layout manager to place widgets in the frame
        self.enter_sides.grid(row=0, column=0)
        self.btn_calculate_angles.grid(row=1, column=0)

        self.enter_inches.grid(row=0, column=1)
        self.btn_calculate_perimeter.grid(row=1, column=1)

        self.lbl_interior.grid(row=2, column=1)
        self.lbl_exterior.grid(row=3, column=1)
        self.lbl_perimeter.grid(row=4,column=1)

        # Set padding between frame and window
        self.main_frame.grid_configure(padx=2, pady=2)
        self.sub_frame.grid_configure(padx=2,pady=2)
        self.third_frame.grid_configure(padx=2,pady=2)
        # set padding for all widgets in the frame
        for widget in self.main_frame.winfo_children():
            widget.grid_configure(padx=2, pady=2)

        for widget in self.sub_frame.winfo_children():
            widget.grid_configure(padx=2, pady=2)

        for widget in self.third_frame.winfo_children():
            widget.grid_configure(padx=2, pady=2)

        # Start the program with focus on the entry widget
        self.enter_sides.focus_set()

        # Bind the enter key to the calculate method
        # When the enter key is pressed,
        # the calculate method will be fired
        self.window.bind('<Return>', self.calculate_angle)





# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()
