# Import the EasyGoPiGo3 library
import easygopigo3 as easy
import time     # import the time library for the sleep function

# Initialize a EasyGoPiGo3 object
GPG = easy.EasyGoPiGo3()

GPG.set_motor_dps(GPG.MOTOR_LEFT | GPG.MOTOR_RIGHT, 100)
start = time.time()
lapse = 0
while lapse < 5:
    lapse = time.time() - start
    time.sleep(0.5)
    print("LEFT: {}  RIGHT:{}".format(GPG.get_motor_status(
        GPG.MOTOR_LEFT), GPG.get_motor_status(GPG.MOTOR_RIGHT)))

passed_test = GPG.get_motor_status(GPG.MOTOR_LEFT)[
    0] == 0 and GPG.get_motor_status(GPG.MOTOR_RIGHT)[0] == 0
GPG.set_motor_dps(GPG.MOTOR_LEFT | GPG.MOTOR_RIGHT, 0)

if passed_test:
    print("Test passed.")
else:
    print("Test failed.")
