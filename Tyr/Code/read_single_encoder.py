# Description: This code reads the position of a rotary encoder and prints it in degrees.

# Import necessary modules
from time import sleep  # Used to add delays in the program
import board            # Provides access to board-specific pin definitions
import rotaryio         # Library to work with rotary encoders

# Encoder constants
# The gear ratio of the motor (how many times the motor shaft rotates for one output shaft rotation)
GEAR_RATIO = 50
# The total counts per revolution of the motor's output shaft
# This is calculated as the encoder's counts per revolution multiplied by the gear ratio
COUNTS_PER_REV = 12 * GEAR_RATIO

# Create the encoder object
# This sets up the rotary encoder using the specified pins on the board
# ENCODER_A_B and ENCODER_A_A are the two pins connected to the encoder
# The divisor is set to 1, meaning no additional scaling
# is applied to the encoder's output
enc_a = rotaryio.IncrementalEncoder(
    board.ENCODER_A_B, board.ENCODER_A_A, divisor=1
)


def to_degrees(position):
    """Convert encoder position to degrees"""
    # Multiply the position by 360 (degrees in a circle) and divide by the total counts per revolution
    return (position * 360.0) / COUNTS_PER_REV


while True:
    # Print out the angle of the encoder in degrees
    # The `position` property of the encoder gives the current count
    for i in range(board.NUM_ENCODERS):  # Loop through all encoders (if there are multiple)
        # Convert the position to degrees and print it
        print(f"= {to_degrees(enc_a.position)}")

    print()  # Print a blank line for readability

    sleep(0.1)  # Pause for 0.1 seconds before repeating the loop
