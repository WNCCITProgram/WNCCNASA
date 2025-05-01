#!./venv/bin/python
from pyPS4Controller.controller import Controller
import smbus
from adafruit_servokit import ServoKit
from time import sleep
from math import tan, atan, degrees, radians

bus = smbus.SMBus(1)
motor2040R = 0x44
motor2040L = 0x48
R_ANGLE = 52  # calc from the rover dimentions
R_COEF = 0.624  # calc from the rover dimentions
MAX_RANGE = 180
HALF_RANGE = MAX_RANGE // 2
COEF = 32767 // HALF_RANGE
_dr = 255  # distance between the opposite wheels
_a = 160  # distance between the adjacent wheels
servos = None
try:
    kit = ServoKit(channels=16)
    servos = [kit.servo[i] for i in range(6)]
    for i in range(6):
        servos[i].set_pulse_width_range(min_pulse=470, max_pulse=2520)
        servos[i].actuation_range = MAX_RANGE
        servos[i].angle = HALF_RANGE
except ValueError:
    print("Servo controller is not connected")


class MyController(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.car_mode = True  # car/parallel
        self.rover_mode = False  # static turn
        self.v0 = 0  # original speed from controller
        self.v1 = 0
        self.v2 = 0
        self.v3 = 0
        self.alpha = 0  # original angle from controller
        self.beta = 0

    def straight(self):
        if not servos:
            return False
        for i in range(6):
            servos[i].angle = HALF_RANGE
        sleep(1)  # let servos complete turn
        return True

    def spin(self, controller, reg, val):
        try:
            bus.write_i2c_block_data(controller, reg, val)
        except OSError:
            print("motor2040 is not connected")

    def car_calc(self):
        """Calculate the secondary wheel angle and speeds for car mode"""
        # these are the most complicated calculations here
        alpha = abs(self.alpha)
        v0 = abs(self.v0)
        if alpha < 3:  # threshold and avoid zero division
            self.beta = alpha
            self.v1 = self.v2 = self.v3 = v0
            return True
        r = _a / tan(radians(alpha))
        r_ = (r**2 + _a**2) ** 0.5
        R = r + _dr
        R_ = (R**2 + _a**2) ** 0.5
        coef = v0 / R_
        self.beta = round(degrees(atan(_a / R)))
        self.v1 = round(R * coef)
        self.v2 = round(r_ * coef)
        self.v3 = round(r * coef)

    def car_turn(self):
        if not servos:
            return False
        if self.alpha > 0:  # turn right
            servos[0].angle = HALF_RANGE + self.alpha
            servos[2].angle = HALF_RANGE - self.alpha
            servos[3].angle = HALF_RANGE + self.beta
            servos[5].angle = HALF_RANGE - self.beta
        else:  # turn left
            servos[0].angle = HALF_RANGE - self.beta
            servos[2].angle = HALF_RANGE + self.beta
            servos[3].angle = HALF_RANGE + self.alpha
            servos[5].angle = HALF_RANGE - self.alpha

    def car_move(self):
        v0 = self.v0
        i = 1
        if self.v0 < 0:
            v0 = -v0
            i = 0
        c1, c2 = motor2040L, motor2040R
        if self.alpha > 0:
            c2, c1 = motor2040L, motor2040R
        self.spin(c1, 0x00 + i, [self.v2])
        self.spin(c1, 0x02 + i, [self.v3])
        self.spin(c1, 0x04 + i, [self.v2])
        self.spin(c2, 0x00 + i, [v0])
        self.spin(c2, 0x02 + i, [self.v1])
        self.spin(c2, 0x04 + i, [v0])

    def rover_turn(self):
        if not servos:
            return False
        servos[0].angle = HALF_RANGE - R_ANGLE
        servos[1].angle = HALF_RANGE
        servos[2].angle = HALF_RANGE + R_ANGLE
        servos[3].angle = HALF_RANGE + R_ANGLE
        servos[4].angle = HALF_RANGE
        servos[5].angle = HALF_RANGE - R_ANGLE
        sleep(1)  # let the servos complete turn
        return True  # switch successful

    def rover_move(self):
        v0 = self.v0
        c1, c2 = motor2040L, motor2040R
        if self.v0 < 0:
            v0 = -v0
            c2, c1 = motor2040L, motor2040R
        v1 = round(v0 * R_COEF)
        self.spin(c1, 0x00, [v0])
        self.spin(c1, 0x02, [v1])
        self.spin(c1, 0x04, [v0])
        self.spin(c2, 0x01, [v0])
        self.spin(c2, 0x03, [v1])
        self.spin(c2, 0x05, [v0])

    def turning(self):
        if self.rover_mode:
            return False
        if self.car_mode:
            self.car_calc()
            self.car_turn()
            self.car_move()  # important to set a new calculated speed
        elif servos:  # parallel
            for i in range(6):
                servos[i].angle = HALF_RANGE + self.alpha

    def driving(self):
        if self.rover_mode:
            self.rover_move()
        elif self.car_mode:
            self.car_calc()
            self.car_move()
        else:  # parallel
            v0 = self.v0
            i = 1
            if self.v0 < 0:
                v0 = -v0
                i = 0
            c1, c2 = motor2040L, motor2040R
            self.spin(c1, 0x00 + i, [v0])
            self.spin(c1, 0x02 + i, [v0])
            self.spin(c1, 0x04 + i, [v0])
            self.spin(c2, 0x00 + i, [v0])
            self.spin(c2, 0x02 + i, [v0])
            self.spin(c2, 0x04 + i, [v0])

    def on_R3_down(self, value):
        # Max value of remote range is 32767
        # This calculation is needed because numbers from the range of 0 - 255 can be used when determining wheel speed
        value /= 128  # Brings number down to the 255 range
        value += 51  # Adds 51 to change the beginning of range
        value /= 1.2  # Brings number back down to 255 range
        value = int(value)  # the bus only takes whole numbers
        # Gives the controller a dead zone which helps the wheel stop
        if value < 50:
            value = 0
        self.v0 = value
        self.driving()

    def on_R3_up(self, value):
        # Max value of remote is -32767
        value /= 128  # Brings number down to the 255 range
        value -= 51  # Adds 51 to bring to to 306
        value /= 1.2  # Brings number back down to 255 range
        value = int(value)  # the bus only takes whole numbers
        if value > -50:
            value = 0
        self.v0 = value  # it is negative
        self.driving()

    def on_R3_left(self, value):
        value //= COEF
        value += 1
        self.alpha = value  # it is negative
        self.turning()

    def on_R3_right(self, value):
        value //= COEF
        self.alpha = value
        self.turning()

    def on_x_press(self):  # switch between car/parallel modes
        self.stop()
        if self.straight():
            self.car_mode = not self.car_mode

    def on_circle_press(self):  # switch rover mode
        self.stop()
        if self.rover_mode:
            self.rover_mode = not self.straight()
        else:
            self.rover_mode = self.rover_turn()

    def stop(self):
        self.v0 = self.v1 = self.v2 = self.v3 = 0
        self.car_move()  # to make sure it stopped


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
# you can start listening before controller is paired, as long as you pair it within the timeout window
controller.listen(timeout=60, on_disconnect=controller.stop())
