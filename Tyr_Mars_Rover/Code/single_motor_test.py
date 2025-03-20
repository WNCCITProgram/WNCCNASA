
# CircuitPython code to drive a single motor using the motor2040 board
# This code is based on the example code from the Pimoroni GitHub repository
# https://github.com/pimoroni/pico-circuitpython-examples/tree/main/motor2040

import time
import board
import pwmio
import digitalio
# Copy the adafruit_motor library folder to the lib folder on the pico
from adafruit_motor import motor

# Pins of the motor to drive
MOTOR_P = board.MOTOR_A_P
MOTOR_N = board.MOTOR_A_N

# Motor constants
FREQUENCY = 25000               # Chose a frequency above human hearing
DECAY_MODE = motor.SLOW_DECAY   # The decay mode affects how the motor
                                # responds, with SLOW_DECAY having improved spin
                                # threshold and speed-to-throttle linearity

# Create the pwm and motor objects
pwm_p = pwmio.PWMOut(MOTOR_P, frequency=FREQUENCY)
pwm_n = pwmio.PWMOut(MOTOR_N, frequency=FREQUENCY)
mot = motor.DCMotor(pwm_p, pwm_n)

# Set the motor decay modes (if unset the default will be FAST_DECAY)
mot.decay_mode = DECAY_MODE


print("Forward slow")
mot.throttle = 0.5
time.sleep(1)

print("Stop")
mot.throttle = 0
time.sleep(1)

print("Forward fast")
mot.throttle = 1.0
time.sleep(1)

print("Spin freely")
mot.throttle = None
time.sleep(1)

print("Backwards slow")
mot.throttle = -0.5
time.sleep(1)

print("Stop")
mot.throttle = 0
time.sleep(1)

print("Backwards fast")
mot.throttle = -1.0
time.sleep(1)

print("Spin freely")
mot.throttle = None
time.sleep(1)
