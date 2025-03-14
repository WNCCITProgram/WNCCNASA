# This code is based on the example code from the Pimoroni GitHub repository for the motor2040 library.
# https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/motor2040
# MicroPython code to demonstrate how to control a motor using the motor2040 library

import time
import math
from motor import Motor, motor2040

"""
Demonstrates how to create a Motor object and control it.
"""

# Create a motor
m = Motor(motor2040.MOTOR_A)

# Enable the motor
m.enable()
time.sleep(2)

print("Drive at 0.5")
m.speed(0.5)
time.sleep(2)

print("Stop moving")
m.stop()
time.sleep(2)

print("Drive at -0.5")
m.speed(-0.5)
time.sleep(2)

print("Coast to a gradual stop")
m.coast()
time.sleep(2)


# SWEEPS = 2              # How many speed sweeps of the motor to perform
# STEPS = 10              # The number of discrete sweep steps
# STEPS_INTERVAL = 0.5    # The time in seconds between each step of the sequence
# SPEED_EXTENT = 1.0      # How far from zero to drive the motor when sweeping
# 
# print("Do a sine speed sweep")
# for j in range(SWEEPS):
#     for i in range(360):
#         m.speed(math.sin(math.radians(i)) * SPEED_EXTENT)
#         time.sleep(0.02)
# 
# print("Do a stepped speed sweep")
# for j in range(SWEEPS):
#     for i in range(0, STEPS):
#         m.to_percent(i, 0, STEPS, 0.0 - SPEED_EXTENT, SPEED_EXTENT)
#         time.sleep(STEPS_INTERVAL)
#     for i in range(0, STEPS):
#         m.to_percent(i, STEPS, 0, 0.0 - SPEED_EXTENT, SPEED_EXTENT)
#         time.sleep(STEPS_INTERVAL)

# Disable the motor
m.disable()