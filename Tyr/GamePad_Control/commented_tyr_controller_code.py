# Import necessary libraries
# pip install pyPS4Controller
from pyPS4Controller.controller import Controller  # For handling PS4 controller inputs
# pip install smbus
import smbus  # For I2C communication
# pip install adafruit-circuitpython-servokit
from adafruit_servokit import ServoKit  # For controlling servo motors
from time import sleep  # For adding delays
from math import pi, tan, atan, degrees, radians  # For mathematical calculations
from threading import Thread  # For running tasks in parallel

# Initialize I2C bus (bus 1 is commonly used on Raspberry Pi)
bus = smbus.SMBus(1)

# Address of the motor controller (replace with the actual address of your device)
motor2040_addr = 0x44

# Constants for servo motor configuration
MAX_RANGE = 180  # Maximum range of servo angles
HALF_RANGE = MAX_RANGE // 2  # Half of the maximum range
COEF = 32767 // HALF_RANGE  # Coefficient for scaling controller input
_dr = 100  # Distance between opposite wheels (adjust based on your setup)
_a = 100  # Distance between adjacent wheels (adjust based on your setup)

# Initialize servo motors
servos = None
try:
    # Create a ServoKit object for controlling up to 16 servos
    kit = ServoKit(channels=16)
    # Initialize 6 servos
    servos = [kit.servo[i] for i in range(6)]
    for i in range(6):
        # Set the pulse width range for the servos
        servos[i].set_pulse_width_range(min_pulse=470, max_pulse=2520)
        # Set the actuation range of the servos
        servos[i].actuation_range = MAX_RANGE
        # Set the initial angle of the servos to the middle position
        servos[i].angle = HALF_RANGE
except ValueError:
    # Print an error message if the servo controller is not connected
    print("Servo controller is not connected")


# Define a custom controller class that extends the PS4 Controller class
class MyController(Controller):
    def __init__(self, **kwargs):
        # Initialize the parent class
        Controller.__init__(self, **kwargs)
        self.car_mode = True  # Set the default mode to "car mode"
        # TODO: Add other modes like "rover" and "parallel"
        self.v0 = 0  # Speed of the main wheel
        self.v1 = 0  # Speed of the first secondary wheel
        self.v2 = 0  # Speed of the second secondary wheel
        self.v3 = 0  # Speed of the third secondary wheel
        self.alpha = 0  # Angle of the main wheel
        self.beta = 0  # Angle of the secondary wheels

    def for_car_mode(self):
        """Calculate the secondary wheel angles and speeds for car mode"""
        # Get the absolute value of the main wheel angle
        alpha = abs(self.alpha)
        # Get the absolute value of the main wheel speed
        v0 = abs(self.v0)
        # If the angle is very small, set all wheels to the same speed
        if alpha < 3:  # Threshold to avoid division by zero
            self.beta = alpha
            self.v1 = self.v2 = self.v3 = v0
            return True
        # Calculate the radius of the turning circle
        r = _a / tan(radians(alpha))
        r_ = (r**2 + _a**2) ** 0.5  # Diagonal distance
        R = r + _dr  # Adjusted radius
        R_ = (R**2 + _a**2) ** 0.5  # Adjusted diagonal distance
        # Calculate the angle and speeds for the secondary wheels
        self.beta = round(degrees(atan(_a / R)))
        self.v1 = round(v0 * R / R_)
        self.v2 = round(v0 * r_ / R_)
        self.v3 = round(v0 * r / R_)

    def move(self):
        """Send speed data to the motor controller"""
        v0 = self.v0  # Get the main wheel speed
        i = 1  # Default direction (forward)
        if self.v0 < 0:  # If the speed is negative, reverse direction
            v0 = -v0
            i = 0
        try:
            # Send speed data to the motor controller via I2C
            # TODO: Add support for a second motor controller and turning
            bus.write_i2c_block_data(motor2040_addr, 0x00 + i, [v0])
            bus.write_i2c_block_data(motor2040_addr, 0x02 + i, [self.v1])
            bus.write_i2c_block_data(motor2040_addr, 0x04 + i, [v0])
        except OSError:
            # Print an error message if the motor controller is not connected
            print("motor2040 is not connected")

    def on_R3_down(self, value):
        """Handle the right joystick being pushed down"""
        # Scale the joystick value to a range of 0-255
        value /= 128
        value += 51
        value /= 1.2
        value = int(value)
        # Apply a dead zone to stop the wheel
        if value < 50:
            value = 0
        self.v0 = value  # Set the main wheel speed
        self.for_car_mode()  # Update the secondary wheels
        self.move()  # Send the speed data to the motor controller
        print(value)  # Print the value for debugging

    def on_R3_up(self, value):
        """Handle the right joystick being pushed up"""
        # Scale the joystick value to a range of 0-255
        value /= 128
        value -= 51
        value /= 1.2
        value = int(value)
        # Apply a dead zone to stop the wheel
        if value > -50:
            value = 0
        self.v0 = value  # Set the main wheel speed
        self.for_car_mode()  # Update the secondary wheels
        self.move()  # Send the speed data to the motor controller
        print(value)  # Print the value for debugging

    def on_R3_y_at_rest(self):
        """Stop the controller when the joystick is at rest"""
        self.v0 = 0  # Set the main wheel speed to 0
        self.for_car_mode()  # Update the secondary wheels
        self.move()  # Send the stop command to the motor controller
        print("Stop")  # Print a message for debugging

    def on_R3_left(self, value):
        """Handle the right joystick being pushed left"""
        value //= COEF  # Scale the joystick value
        value += 1
        self.alpha = value  # Set the main wheel angle
        self.for_car_mode()  # Update the secondary wheels
        print(self.alpha, self.beta, self.v0, self.v1, self.v2, self.v3)  # Debug info
        alpha = HALF_RANGE + self.alpha  # Adjust the angle for the servo
        beta = HALF_RANGE - self.beta  # Adjust the angle for the servo
        if servos:
            # TODO: Send the angle to all servos
            servos[0].angle = beta
            servos[1].angle = alpha
        self.move()  # Send the speed data to the motor controller

    def on_R3_right(self, value):
        """Handle the right joystick being pushed right"""
        value //= COEF  # Scale the joystick value
        self.alpha = value  # Set the main wheel angle
        self.for_car_mode()  # Update the secondary wheels
        print(self.alpha, self.beta, self.v0, self.v1, self.v2, self.v3)  # Debug info
        alpha = HALF_RANGE + self.alpha  # Adjust the angle for the servo
        beta = HALF_RANGE + self.beta  # Adjust the angle for the servo
        if servos:
            # TODO: Send the angle to all servos
            servos[0].angle = alpha
            servos[1].angle = beta
        self.move()  # Send the speed data to the motor controller

    def send_data(self):
        """Continuously send data (placeholder for future functionality)"""
        while True:
            sleep(0.01)  # Add a small delay to avoid overloading the system


# Create an instance of the custom controller
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
# Start listening for controller inputs (pair the controller within the timeout window)
controller.listen(timeout=60)