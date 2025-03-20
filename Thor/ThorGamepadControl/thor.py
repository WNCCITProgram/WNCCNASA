from time import sleep
from my_serial import serial_write
import keys

# Movement limits
CLAW_MIN = 0
CLAW_MAX = 500
CLAW_ROT_MIN = -13
CLAW_ROT_MAX = 13
CLAW_MOVE_MIN = -5
CLAW_MOVE_MAX = 5
ART4_MIN = -90
ART4_MAX = 90
ART3_MIN = -90
ART3_MAX = 90
ART2_MIN = -90
ART2_MAX = 90
ART1_MIN = -90
ART1_MAX = 90


class Thor:
    def __init__(self) -> None:
        self.event = ""
        # current positions
        self.claw = 500
        self.y = 0
        self.z = 0
        self.claw_rot = 0
        self.claw_move = 0
        self.art4 = 0
        self.art3 = 0
        self.art2 = 0
        self.art1 = 0

    def open_claw(self):
        while self.claw < CLAW_MAX and self.event != keys._L2 and self.event:
            self.claw += 1
            serial_write(f"M3 S{self.claw}")

    def close_claw(self):
        while self.claw > CLAW_MIN and self.event != keys._L1 and self.event:
            self.claw -= 1  # step can be adjustable
            serial_write(f"M3 S{self.claw}")
            sleep(0.002)  # can be adjustable

    def rotate_claw(self):
        while self.claw_rot < CLAW_ROT_MAX and self.event != keys._RIGHT and self.event:
            self.claw_rot += 1
            # y and x are needed to track positions for claw move and rotate functions together
            self.y += 1
            self.z += 1
            serial_write(f"G0 Y{self.y} Z{self.z}")
            sleep(0.1)

    def rotate_claw_cw(self):
        while self.claw_rot > CLAW_ROT_MIN and self.event != keys._LEFT and self.event:
            self.claw_rot -= 1
            self.y -= 1
            self.z -= 1
            serial_write(f"G0 Y{self.y} Z{self.z}")
            sleep(0.1)

    def move_claw(self):
        while (
            self.claw_move < CLAW_MOVE_MAX and self.event != keys._DOWN and self.event
        ):
            self.claw_move += 0.1
            self.y -= 0.1
            self.z += 0.1
            serial_write(f"G0 Y{self.y} Z{self.z}")
            sleep(0.02)

    def move_claw_b(self):
        while self.claw_move > CLAW_MOVE_MIN and self.event != keys._UP and self.event:
            self.claw_move -= 0.1
            self.y += 0.1
            self.z -= 0.1
            serial_write(f"G0 Y{self.y} Z{self.z}")
            sleep(0.02)

    def art_4(self):  # wrist rotation
        while self.art4 < ART4_MAX and self.event != keys._A_2 and self.event:
            self.art4 += 2
            serial_write(f"G0 X{self.art4}")
            sleep(0.1)

    def art_4_cw(self):
        while self.art4 > ART4_MIN and self.event != keys._Y_4 and self.event:
            self.art4 -= 2
            serial_write(f"G0 X{self.art4}")
            sleep(0.1)

    def art_3(self):  # elbow
        while self.art3 < ART3_MAX and self.event != keys._X_1 and self.event:
            self.art3 += 1
            serial_write(f"G0 D{self.art3}")
            sleep(0.1)

    def art_3_b(self):
        while self.art3 > ART3_MIN and self.event != keys._B_3 and self.event:
            self.art3 -= 1
            serial_write(f"G0 D{self.art3}")
            sleep(0.1)

    def art_2(self):  # shoulder
        while self.art2 < ART2_MAX and self.event != keys._R2 and self.event:
            self.art2 += 1
            serial_write(f"G0 B{self.art2} C{self.art2}")
            sleep(0.1)

    def art_2_b(self):
        while self.art2 > ART2_MIN and self.event != keys._R1 and self.event:
            self.art2 -= 1
            serial_write(f"G0 B{self.art2} C{self.art2}")
            sleep(0.1)

    def art_1(self):  # rotate arm
        while self.art1 < ART1_MAX and self.event != keys._L_AN and self.event:
            self.art1 += 2
            serial_write(f"G0 A{self.art1}")
            sleep(0.1)

    def art_1_cw(self):
        while self.art1 > ART1_MIN and self.event != keys._R_AN and self.event:
            self.art1 -= 2
            serial_write(f"G0 A{self.art1}")
            sleep(0.1)

    def home(self):
        serial_write("M3 S500")
        serial_write("G1 A0 B0 C0 D0 X0 Y0 Z0 F500")
        self.claw = 500
        self.y = self.z = self.claw_rot = self.claw_move = 0
        self.art4 = self.art3 = self.art2 = self.art1 = 0
