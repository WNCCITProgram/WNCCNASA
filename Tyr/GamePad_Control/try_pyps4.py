from pyPS4Controller.controller import Controller
import smbus
from adafruit_servokit import ServoKit
from time import sleep

bus = smbus.SMBus(1)  # Use I2C bus 1
motor2040_addr = 0x44  # Replace with actual address
MAX_RANGE = 130
HALF_RANGE = MAX_RANGE // 2
COEF = 32767 // HALF_RANGE
servos = None
try:
    kit = ServoKit(channels=16)
    servos = [kit.servo[i] for i in range(6)]
    for i in range(6):
        servos[i].actuation_range = MAX_RANGE
        servos[i].angle = HALF_RANGE
except ValueError:
    print("Servo controller is not connected")


class MyController(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

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
        try:
            bus.write_i2c_block_data(motor2040_addr, 0x01, [value])  # Register 0x01
        except OSError:
            print("motor2040 is not connected")
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
        try:
            bus.write_i2c_block_data(motor2040_addr, 0x00, [value])  # Register 0x00
        except OSError:
            print("motor2040 is not connected")
        # Retuns value for trouble shooting
        print(value)

    # Stops the controller when the thumb stick is at rest
    def on_R3_y_at_rest(self):
        try:
            bus.write_i2c_block_data(motor2040_addr, 0x00, [0])  # Register 0x00
        except OSError:
            print("motor2040 is not connected")
        print("Stop")

    def on_L3_up(self, value):
        print(value)

    def on_L3_down(self, value):
        print(value)

    def on_L3_left(self, value):
        value *= -1
        value //= COEF
        value = HALF_RANGE - value
        print(value)
        if servos:
            servos[0].angle = value

    def on_L3_right(self, value):
        value //= COEF
        value += HALF_RANGE
        print(value)
        if servos:
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
