"""
Simple test for a standard servo on channel 0
and a continuous rotation servo on channel 1.
"""

from time import sleep

# https://pypi.org/project/adafruit-circuitpython-servokit/
# pip install adafruit-circuitpython-servokit
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.

kit = ServoKit(channels=16)

print("Setting standard servo on channel 0 180 degrees")
kit.servo[0].angle = 180

sleep(1)

print("Setting standard servo on channel 0 0 degrees")
kit.servo[0].angle = 0

sleep(1)

print("Setting standard servo on channel 0 90 degrees")
kit.servo[0].angle = 90

sleep(1)
