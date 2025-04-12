import time
import board
from i2ctarget import I2CTarget
import pwmio
from adafruit_motor import motor

FREQUENCY = 25000  # Chose a frequency above human hearing
DECAY_MODE = motor.SLOW_DECAY  # The decay mode affects how the motor behaves
pwm_ap = pwmio.PWMOut(board.MOTOR_A_P, frequency=FREQUENCY)
pwm_an = pwmio.PWMOut(board.MOTOR_A_N, frequency=FREQUENCY)
pwm_bp = pwmio.PWMOut(board.MOTOR_B_P, frequency=FREQUENCY)
pwm_bn = pwmio.PWMOut(board.MOTOR_B_N, frequency=FREQUENCY)
pwm_cp = pwmio.PWMOut(board.MOTOR_C_P, frequency=FREQUENCY)
pwm_cn = pwmio.PWMOut(board.MOTOR_C_N, frequency=FREQUENCY)
motA = motor.DCMotor(pwm_ap, pwm_an)
motB = motor.DCMotor(pwm_bp, pwm_bn)
motC = motor.DCMotor(pwm_cp, pwm_cn)
motA.decay_mode = DECAY_MODE
motB.decay_mode = DECAY_MODE
motC.decay_mode = DECAY_MODE

# Set Motor2040 as an I2C slave at address 0x44
with I2CTarget(board.SCL, board.SDA, (0x44,)) as device:
    reg = None
    while True:
        try:
            i2c_target_request = device.request()
            if not i2c_target_request:
                continue  # No request, loop again
            with i2c_target_request:
                data = i2c_target_request.read(1)
                # separate register and data
                if reg is None:
                    reg = data[0]
                    continue
                val = data[0]
                val /= 255
                if reg == 0:
                    motA.throttle = val
                elif reg == 1:  # reg = 1 for backward
                    motA.throttle = -val
                elif reg == 2:
                    motB.throttle = val
                elif reg == 3:
                    motB.throttle = -val
                elif reg == 4:
                    motC.throttle = val
                elif reg == 5:
                    motC.throttle = -val
                print(reg, val)
                reg = None
        except Exception as e:
            print(e)
