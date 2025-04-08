from pyPS4Controller.controller import Controller
import smbus
from adafruit_servokit import ServoKit
from time import sleep
from math import pi, tan, atan, degrees, radians

bus = smbus.SMBus(1)  # Use I2C bus 1
motor2040_addr = 0x44  # Replace with actual address
MAX_RANGE = 130
HALF_RANGE = MAX_RANGE // 2
COEF = 32767 // HALF_RANGE
_dr = 100  # distance between the opposite wheels, adjust after assembling
_a = 100  # distance between the adjacent wheels, adjust after assembling
servos = None
try:
    kit = ServoKit(channels=16)
    servos = [kit.servo[i] for i in range(6)]
    for i in range(6):
        servos[i].actuation_range = MAX_RANGE
        servos[i].angle = HALF_RANGE
except ValueError:
    print("Servo controller is not connected")


def move(reg: int, value: int):
    try:
        bus.write_i2c_block_data(motor2040_addr, reg, [value])
    except OSError:
        print("motor2040 is not connected")


class MyController(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.car_mode = True
        # TODO: add other modes: rover and parallel
        self.v1 = 0
        self.v2 = 0
        self.v3 = 0
        self.beta = 0

    def for_car_mode(self, v0, alpha):
        """Calculate the secondary wheel angle and speeds for car mode"""
        # these are the most complicated calculations here
        if alpha < 3:  # threshold and avoid zero division
            self.beta = alpha
            self.v1 = self.v2 = self.v3 = v0
            return True
        r = _a / tan(radians(alpha))
        r_ = (r**2 + _a**2) ** 0.5
        R = r + _dr
        R_ = (R**2 + _a**2) ** 0.5
        self.beta = round(degrees(atan(_a / R)))
        self.v1 = round(v0 * R / R_)
        self.v2 = round(v0 * r_ / R_)
        self.v3 = round(v0 * r / R_)

    def on_x_press(self):
        print("Hello world")

    def on_x_release(self):
        print("Goodbye world")

    def on_R3_down(self, value):
        # Max value of remote range is 32767
        # This calculation is needed because numbers from the range of 0 - 255 can be used when determining wheel speed
        value /= 128  # Brings number down to the 255 range
        value += 51  # Adds 51 to change the beginning of range
        value /= 1.2  # Brings number back down to 255 range
        value = int(
            value
        )  # Gets rid of decimal points because the bus only takes whole numbers
        # Gives the controller a dead zone which helps the wheel stop
        if value < 50:
            value = 0
        # Makes the wheel turn the speed of the value given by controller
        move(0x01, value)  # register 1 - backward
        # TODO: move all motors
        # Retuns value for trouble shooting
        print(value)

    def on_R3_up(self, value):
        # Max value of remote is -32767
        # We do this to make the number positive for the wheel speed.
        value *= -1
        # Max value of remote range is 32767
        # This calculation is needed because numbers from the range of 0 - 255 can be used when determining wheel speed
        value /= 128  # Brings number down to the 255 range
        value += 51  # Adds 51 to bring to to 306
        value /= 1.2  # Brings number back down to 255 range
        value = int(
            value
        )  # Gets rid of decimal points because the bus only takes whole numbers
        # Gives the controller a dead zone for the wheel to stop
        if value < 50:
            value = 0
        # Makes the wheel turn the speed of the value given by controller
        move(0x00, value)  # register 0 - forward
        # TODO: move all motors
        # Retuns value for trouble shooting
        print(value)

    # Stops the controller when the thumb stick is at rest
    def on_R3_y_at_rest(self):
        move(0x00, 0)
        print("Stop")

    def on_L3_up(self, value):
        print(value)

    def on_L3_down(self, value):
        print(value)

    def on_L3_left(self, value):
        value *= -1
        value //= COEF
        ###########################################
        self.for_car_mode(100, value)
        # 100 is for demonstration. It will splitted to speed and angle for car_mode separated functions
        print(value, self.beta, 100, self.v1, self.v2, self.v3)
        ###########################################
        value = HALF_RANGE - value
        # print(value)
        if servos:
            # TODO: send angle to all servos
            servos[0].angle = value

    def on_L3_right(self, value):
        value //= COEF
        ###########################################
        self.for_car_mode(100, value)
        # 100 is for demonstration. It will splitted to speed and angle for car_mode separated functions
        print(value, self.beta, 100, self.v1, self.v2, self.v3)
        ###########################################
        value += HALF_RANGE
        # print(value)
        if servos:
            # TODO: send angle to all servos
            servos[0].angle = value

    def on_R3_left(self, value):
        # print(value)
        pass

    def on_R3_right(self, value):
        # print(value)
        pass


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
# you can start listening before controller is paired, as long as you pair it within the timeout window
controller.listen(timeout=60)
