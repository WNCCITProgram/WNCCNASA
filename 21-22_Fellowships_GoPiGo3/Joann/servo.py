#--------------------------------- IMPORTS -------------------------------------#
import time                             # Import the time library for the sleep function
import easygopigo3 as easy              # Import the GoPiGo3 library


#--------------------------------- INITIALIZE GOPIGO -------------------------------------#
gpg = easy.EasyGoPiGo3()          # Initialize EasyGoPiGo3 object
servo = gpg.init_servo("SERVO1")  # Initialize servo object on Servo Port 1

# Set servo pointing straight ahead at 90 degrees
# You may have to change the degrees to adapt to your servo
# All servos line up slightly differently
servo.rotate_servo(90)
print("Forward")
time.sleep(1)


#--------------------------------- MAIN PROGRAM -------------------------------------#
def main():
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

    # Disable or "float" the servo
    servo.disable_servo()


# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()