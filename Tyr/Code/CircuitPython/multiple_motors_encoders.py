"""
    Filename: test_motor_and_encoder.py
    Description: CircuitPython code to drive a single motor 
    and read encoder values using OOP.
"""

# Import necessary libraries
import time  # For delays and timing
import board  # For accessing board pins
import pwmio  # For generating PWM signals
import rotaryio  # For reading rotary encoders
from adafruit_motor import motor  # For motor control

# Timers are for the motor run time
TIMER_LONG = 15
TIMER_SHORT = 5
# These change the speed of the motors used in the main function 
FORWARD_FAST = 1
FORWARD_SLOW = .5
BACKWARD_FAST = -1
BACKWARD_SLOW= -.5

class MotorWithEncoder:
    """
    A class to control a motor and read its encoder values.
    """

    def __init__(self, motor_p_pin, motor_n_pin, encoder_a_pin, encoder_b_pin, gear_ratio, frequency=25000):
        """
        Initialize the motor and encoder.

        Parameters:
        - motor_p_pin: The positive motor pin.
        - motor_n_pin: The negative motor pin.
        - encoder_a_pin: The encoder channel A pin.
        - encoder_b_pin: The encoder channel B pin.
        - gear_ratio: The gear ratio of the motor.
        - frequency: The PWM frequency for motor control (default is 25 kHz).
        """
        # Motor setup
        self.pwm_p = pwmio.PWMOut(motor_p_pin, frequency=frequency)
        self.pwm_n = pwmio.PWMOut(motor_n_pin, frequency=frequency)
        self.motor = motor.DCMotor(self.pwm_p, self.pwm_n)

        # The decay mode affects how the motor slows down when
        # the PWM signal is turned off.
        # FAST_DECAY is the default mode.
        # SLOW_DECAY is used for more precise control of the motor speed
        self.motor.decay_mode = motor.SLOW_DECAY

        # Encoder setup
        self.encoder = rotaryio.IncrementalEncoder(
            encoder_b_pin, encoder_a_pin, divisor=1
        )

        # Constants
        self.gear_ratio = gear_ratio
        # Total counts per revolution of the motor's output shaft
        self.counts_per_rev = 12 * gear_ratio

# ------------------------------ TO DEGREES -------------------------------- #
    def to_degrees(self, position):
        """
        Convert encoder position to degrees.

        Parameters:
        - position: The encoder position.

        Returns:
        - The position in degrees.
        """
        return (position * 360.0) / self.counts_per_rev

# ----------------------------- PERFORM MOVEMENT --------------------------- #
    def perform_movement(self, description, motor_name, throttle, duration):
        """
        Perform a motor movement while reading and displaying encoder values.

        Parameters:
        - description: A string describing the movement (e.g., "Forward slow").
        - throttle: The motor speed (-1.0 for full reverse,
          1.0 for full forward, None for free spin).
        - duration: The duration of the movement in seconds.
        """
        print(motor_name) # Prints the motor name to tell the difference
        print(description)  # Print the description of the movement
        

        self.motor.throttle = throttle  # Set the motor speed

        start_time = time.monotonic()  # Record the start time

        while time.monotonic() - start_time < duration:
            # Loop for the specified duration

            # Read the encoder position and convert it to degrees
            angle = self.to_degrees(self.encoder.position)

            # Print the current encoder angle
            print(f"Encoder Angle ({self}): {angle:.2f} degrees")
            time.sleep(0.1)  # Wait for 0.1 seconds before reading again
        self.motor.throttle = 0  # Stop the motor after the movement


def main():
    """
    Main function to run the motor and encoder test.
    """
    try:
        # Create an instance of the MotorWithEncoder class for Motor A
        motor_with_encoder_A = MotorWithEncoder(
            motor_p_pin=board.MOTOR_A_P,
            motor_n_pin=board.MOTOR_A_N,
            encoder_a_pin=board.ENCODER_A_A,
            encoder_b_pin=board.ENCODER_A_B,
            gear_ratio=50
        )
        
        # Create an instance of the MotorWithEncoder class for Motor B
        motor_with_encoder_B = MotorWithEncoder(
            motor_p_pin=board.MOTOR_B_P,
            motor_n_pin=board.MOTOR_B_N,
            encoder_a_pin=board.ENCODER_B_A,
            encoder_b_pin=board.ENCODER_B_B,
            gear_ratio=50
        )
        # Create an instance of the MotorWithEncoder class for Motor C
        motor_with_encoder_C = MotorWithEncoder(
            motor_p_pin=board.MOTOR_C_P,
            motor_n_pin=board.MOTOR_C_N,
            encoder_a_pin=board.ENCODER_C_A,
            encoder_b_pin=board.ENCODER_C_B,
            gear_ratio=50
        )
    while True:
            # Perform a series of movements with the motor
            # Move forward at 50% speed for 1 second
            motor_with_encoder_A.perform_movement("Forward slow", "Motor_A", FORWARD_FAST, TIMER_LONG)
            motor_with_encoder_B.perform_movement("Forward slow", "Motor_B", FORWARD_FAST, TIMER_LONG)
            motor_with_encoder_C.perform_movement("Forward slow", "Motor_C", FORWARD_FAST, TIMER_LONG)

            # Move forward at full speed for 1 second
            motor_with_encoder_A.perform_movement("Forward fast", "Motor_A", FORWARD_SLOW, TIMER_LONG)
            motor_with_encoder_B.perform_movement("Forward fast", "Motor_B", FORWARD_SLOW, TIMER_LONG)
            motor_with_encoder_C.perform_movement("Forward fast", "Motor_C", FORWARD_SLOW, TIMER_LONG)
            
            # Move backward at 50% speed for 1 second
            motor_with_encoder_A.perform_movement("Backwards slow", "Motor_A", BACKWARD_FAST, TIMER_LONG)
            motor_with_encoder_B.perform_movement("Backwards slow", "Motor_B", BACKWARD_FAST, TIMER_LONG)
            motor_with_encoder_C.perform_movement("Backwards slow", "Motor_C", BACKWARD_FAST, TIMER_LONG)
            
            # Move backward at full speed for 1 second
            motor_with_encoder_A.perform_movement("Backwards fast", "Motor_A", BACKWARD_SLOW, TIMER_LONG)
            motor_with_encoder_B.perform_movement("Backwards fast", "Motor_B", BACKWARD_SLOW, TIMER_LONG)
            motor_with_encoder_C.perform_movement("Backwards fast", "Motor_C", BACKWARD_SLOW, TIMER_LONG)
        

        #Stops the motors
        # motor_with_encoder_A.perform_movement(
            #"Stop", 0, 1)  # Stop the motor for 1 second        
        #motor_with_encoder_B.perform_movement(
            #"Stop", 0, 1)  # Stop the motor for 1 second
        
        
        
        """
        # Move forward at full speed for 1 second
        motor_with_encoder.perform_movement("Forward fast", 1.0, 1)
        # Let the motor spin freely for 1 second
        motor_with_encoder.perform_movement("Spin freely", None, 1)
        # Move backward at 50% speed for 1 second
        motor_with_encoder.perform_movement("Backwards slow", -0.5, 1)
        motor_with_encoder.perform_movement(
            "Stop", 0, 1)  # Stop the motor for 1 second
        # Move backward at full speed for 1 second
        motor_with_encoder.perform_movement("Backwards fast", -1.0, 1)
        # Let the motor spin freely for 1 second
        motor_with_encoder.perform_movement("Spin freely", None, 1)
        """

    except KeyboardInterrupt:
        # Handle the case where the user interrupts the program (e.g., with Ctrl+C)
        print("Stopping motor...")  # Print a message
        motor_with_encoder.motor.throttle = 0  # Stop the motor


if __name__ == "__main__":
    main()