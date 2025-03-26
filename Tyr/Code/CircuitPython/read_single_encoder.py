"""
    File: read_single_encoder.py
    Description: Read the position of a single rotary encoder
    and prints its angle in degrees.

"""

from time import sleep
# Provides access to the board's pin definitions for hardware connections.
import board
# Provides tools to read rotary encoders,
# which measure the rotation of a motor or shaft.
import rotaryio

# Encoder constants
# The gear ratio of the motor
GEAR_RATIO = 50
# The counts per revolution of the motor's output shaft
COUNTS_PER_REV = 12 * GEAR_RATIO

# Create the encoder objects
enc_a = rotaryio.IncrementalEncoder(
    board.ENCODER_A_B, board.ENCODER_A_A, divisor=1)


def to_degrees(position):
    """Convert encoder position to degrees"""
    return (position * 360.0) / COUNTS_PER_REV


while True:
    # Print out the angle of each encoder
    for i in range(board.NUM_ENCODERS):
        print(f"= {to_degrees(enc_a.position)}")

    print()
    sleep(0.1)
