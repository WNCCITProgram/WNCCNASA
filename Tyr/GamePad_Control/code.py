import time
import board
from i2ctarget import I2CTarget
import pwmio
from adafruit_motor import motor

MOTOR_P = board.MOTOR_A_P
MOTOR_N = board.MOTOR_A_N
FREQUENCY = 25000  # Chose a frequency above human hearing
DECAY_MODE = motor.SLOW_DECAY  # The decay mode affects how the motor
pwm_p = pwmio.PWMOut(MOTOR_P, frequency=FREQUENCY)
pwm_n = pwmio.PWMOut(MOTOR_N, frequency=FREQUENCY)
mot = motor.DCMotor(pwm_p, pwm_n)
mot.decay_mode = DECAY_MODE

# Set Motor2040 as an I2C slave at address 0x40
with I2CTarget(board.SCL, board.SDA, (0x40,)) as device:
    reg = None
    while True:
        try:
            i2c_target_request = device.request()
            if not i2c_target_request:
                continue  # No request, loop again
            with i2c_target_request:
                data = i2c_target_request.read(1)
                if reg is None:
                    reg = data[0]
                else:
                    val = data[0]
                    if reg:
                        val *= -1
                    print(reg, val)
                    mot.throttle = val / 255
                    reg = None
        except Exception as e:
            print(e)
