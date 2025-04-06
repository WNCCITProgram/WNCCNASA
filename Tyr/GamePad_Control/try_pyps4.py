from pyPS4Controller.controller import Controller
import smbus
from time import sleep

bus = smbus.SMBus(1)  # Use I2C bus 1
motor2040_addr = 0x40  # Replace with actual address


class MyController(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

    def on_x_press(self):
        print("Hello world")

    def on_x_release(self):
        print("Goodbye world")

    def on_R3_down(self, value):
        value /= 128  # change the range to 0-255
        value += 51
        value /= 1.2  # change the range to 51-255
        value = int(value)
        if value < 50:
            value = 0
        bus.write_i2c_block_data(motor2040_addr, 0x01, [value])
        # Register 0x01 for backward
        print(value)

    def on_R3_up(self, value):
        value *= -1
        value /= 128
        value += 51
        value /= 1.2
        value = int(value)
        if value < 50:
            value = 0
        bus.write_i2c_block_data(motor2040_addr, 0x00, [value])  # Register 0x00
        print(value)

    def on_L3_up(self, value):
        print(value)

    def on_L3_down(self, value):
        print(value)

    def on_L3_left(self, value):
        print(value)

    def on_L3_right(self, value):
        print(value)

    def on_R3_left(self, value):
        # print(value)
        pass

    def on_R3_right(self, value):
        # print(value)
        pass


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
# you can start listening before controller is paired, as long as you pair it within the timeout window
controller.listen(timeout=60)
