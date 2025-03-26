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

    def on_L2_press(self, value):
        print(value)

    def on_R2_press(self, value):
        value += 32767
        value /= 256
        value += 51
        value /= 1.2
        value = int(value)
        bus.write_i2c_block_data(motor2040_addr, 0x00, [value])  # Register 0x00
        print(value)

    def on_R2_release(self):
        bus.write_i2c_block_data(motor2040_addr, 0x00, [1])  # Register 0x00
        print("STOP")

    def on_L3_up(self, value):
        print(value)

    def on_L3_down(self, value):
        print(value)

    def on_L3_left(self, value):
        print(value)

    def on_L3_right(self, value):
        print(value)

    def on_R3_up(self, value):
        print(value)

    def on_R3_down(self, value):
        print(value)

    def on_R3_left(self, value):
        print(value)

    def on_R3_right(self, value):
        print(value)


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
# you can start listening before controller is paired, as long as you pair it within the timeout window
controller.listen(timeout=60)
