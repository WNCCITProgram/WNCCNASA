#!./venv/bin/python
from pyPS4Controller.controller import Controller
import smbus
from adafruit_servokit import ServoKit
from time import sleep
from math import tan, atan, degrees, radians
import shutdown_raspi

bus = smbus.SMBus(1)
RMC = 0x44  # right motor2040 controller addr
LMC = 0x48  # left motor2040 controller addr
R_ANGLE = 52  # calc from the rover dimentions
R_COEF = 0.624  # calc from the rover dimentions
FULL_RANGE = 180
HALF_RANGE = FULL_RANGE // 2  # straight wheels position
COEF = 32767 // HALF_RANGE
DR = 255 / 160  # proportional distance between the opposite wheels
servos = None
try:
    kit = ServoKit(channels=16)
    servos = [kit.servo[i] for i in range(6)]
    for i in range(6):
        servos[i].set_pulse_width_range(min_pulse=470, max_pulse=2520)
        servos[i].actuation_range = FULL_RANGE
        servos[i].angle = HALF_RANGE
except ValueError:
    print("Servo controller is not connected")


class MyController(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.car_mode = True  # car/parallel
        self.onestick = True  # use one stick to control
        self.rover_mode = False  # static turn
        self.v0 = 0  # original speed from controller
        self.v1 = 0
        self.v2 = 0
        self.v3 = 0
        self.alpha = 0  # original angle from controller
        self.beta = 0

    def spin(self, controller, reg, val):
        """Low Level Function to set motor rotation"""
        try:
            bus.write_i2c_block_data(controller, reg, val)
        except OSError:
            print("motor2040 is not connected")

    def straight(self):
        """Set the wheels straight"""
        if not servos:
            return False
        for i in range(6):
            servos[i].angle = HALF_RANGE
        sleep(0.5)  # let servos complete turn
        return True

    ### Car Mode Functions ###

    def car_calc(self):
        """Calculate the secondary wheel angle and speeds for car mode"""
        # these are the most complicated calculations here, 1 is proportional adjacent distance
        alpha = abs(self.alpha)
        v0 = abs(self.v0)
        if alpha < 3:  # threshold and avoid zero division
            self.beta = alpha
            self.v1 = self.v2 = self.v3 = v0
            return True
        r = 1 / tan(radians(alpha))
        r_ = (r**2 + 1) ** 0.5
        R = r + DR
        R_ = (R**2 + 1) ** 0.5
        coef = v0 / R_
        self.beta = round(degrees(atan(1 / R)))
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
        v0 = abs(self.v0)
        c1, c2 = LMC, RMC
        if self.alpha > 0:
            c2, c1 = LMC, RMC
        self.spin(c1, 0x00 + (self.v0 > 0), [self.v2])
        self.spin(c1, 0x02 + (self.v0 > 0), [self.v3])
        self.spin(c1, 0x04 + (self.v0 > 0), [self.v2])
        self.spin(c2, 0x00 + (self.v0 > 0), [v0])
        self.spin(c2, 0x02 + (self.v0 > 0), [self.v1])
        self.spin(c2, 0x04 + (self.v0 > 0), [v0])

    ### Rover Mode Functions ###

    def rover_turn(self):
        if not servos:
            return False
        servos[0].angle = HALF_RANGE - R_ANGLE
        servos[1].angle = HALF_RANGE
        servos[2].angle = HALF_RANGE + R_ANGLE
        servos[3].angle = HALF_RANGE + R_ANGLE
        servos[4].angle = HALF_RANGE
        servos[5].angle = HALF_RANGE - R_ANGLE
        sleep(0.5)  # let the servos complete turn
        return True  # switch successful

    def rover_move(self):
        v0 = abs(self.v0)
        v1 = round(v0 * R_COEF)
        self.spin(LMC, 0x00 + (self.v0 < 0), [v0])
        self.spin(LMC, 0x02 + (self.v0 < 0), [v1])
        self.spin(LMC, 0x04 + (self.v0 < 0), [v0])
        self.spin(RMC, 0x00 + (self.v0 > 0), [v0])
        self.spin(RMC, 0x02 + (self.v0 > 0), [v1])
        self.spin(RMC, 0x04 + (self.v0 > 0), [v0])

    ### High Level Functions ###

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
            v0 = abs(self.v0)
            self.spin(LMC, 0x00 + (self.v0 > 0), [v0])
            self.spin(LMC, 0x02 + (self.v0 > 0), [v0])
            self.spin(LMC, 0x04 + (self.v0 > 0), [v0])
            self.spin(RMC, 0x00 + (self.v0 > 0), [v0])
            self.spin(RMC, 0x02 + (self.v0 > 0), [v0])
            self.spin(RMC, 0x04 + (self.v0 > 0), [v0])

    ### Control Functions ###

    def on_R3_down(self, value):  # max value is 32767
        """Adjust the range to 42 - 255 the bus can use and give the controller a dead zone to stop the wheels"""
        self.v0 = int((value + 6503) / 154) if value > 700 else 0
        self.driving()

    def on_R3_up(self, value):  # the value is negative
        """Adjust the range to (-42) - (-255) the bus can use and give the controller a dead zone to stop the wheels"""
        self.v0 = int((value - 6503) / 154) if value < -700 else 0
        self.driving()

    def on_L3_left(self, value):  # the value is negative
        if not self.onestick:
            self.alpha = 1 + value // COEF
            self.turning()

    def on_L3_right(self, value):
        if not self.onestick:
            self.alpha = value // COEF
            self.turning()

    def on_R3_left(self, value):  # the value is negative
        if self.onestick:
            self.alpha = 1 + value // COEF
            self.turning()

    def on_R3_right(self, value):
        if self.onestick:
            self.alpha = value // COEF
            self.turning()

    ### Switch Functions ###

    def on_x_press(self):  # switch between car/parallel modes
        self.stop
        self.rover_mode = False
        if self.straight():
            self.car_mode = not self.car_mode

    def on_circle_press(self):  # switch rover mode
        self.stop
        if self.rover_mode:
            self.rover_mode = not self.straight()
        else:
            self.rover_mode = self.rover_turn()

    def on_triangle_press(self):  # switch 1 or 2 sticks control
        self.onestick = not self.onestick

    def on_options_press(self):  # For turing the pi off safely
        self.stop
        shutdown_raspi.shutdown_rpi()  # use the imported module

    def stop(self):
        self.v0 = self.v1 = self.v2 = self.v3 = 0
        self.car_move()  # to make sure it stopped


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
# you can start listening before controller is paired, as long as you pair it within the timeout window
controller.listen(timeout=60, on_disconnect=controller.stop)
