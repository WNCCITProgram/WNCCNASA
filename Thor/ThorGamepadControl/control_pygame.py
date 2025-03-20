"""
    Name: control_pygame.py
    Author:
    Created:
    Purpose: Communicate with Thor using a gamepad
"""
# Import the read_thread from my_serial module
from my_serial import read_thread
# Import the Thor class from thor module
from thor import Thor
# Import the Thread class from threading module
from threading import Thread
# Import the pygame module for gamepad control
import pygame
# Import the sleep function from time module
from time import sleep


class GamepadController:
    def __init__(self):
        # Initialize pygame and joystick
        pygame.init()
        pygame.joystick.init()

        # Check if there are any joysticks connected
        if not pygame.joystick.get_count():
            print("No Gamepad!")
            exit(1)

        # Create a Joystick object for the first joystick
        self.joystick = pygame.joystick.Joystick(0)
        # Deprecated since 2.0.0
        # self.joystick.init()

        # Create an instance of the Thor class
        self.thor = Thor()

        # Start the serial listener thread
        read_thread.start()

    def run(self):
        # Keep running while the read_thread is alive
        while read_thread.is_alive():
            try:
                # Sleep for 0.01 seconds
                sleep(0.01)
                event = pygame.event.get()  # Get the list of events
            except KeyboardInterrupt:  # Handle keyboard interrupt
                break  # Break the loop
            if not event:  # If no event, continue to the next iteration
                continue
            ev = event[0]  # Get the first event
            t = ev.type  # Get the type of the event
            # Check if the event is a joystick motion or hat motion
            if t == 1540 or (t == 1538 and ev.value == (0, 0)):
                self.thor.event = ""  # Clear the event
                continue
            btn = None  # Initialize btn as None
            if t == 1539:  # Check if the event is a button press
                btn = ev.button  # Get the button number
            if t == 1538:  # Check if the event is a hat motion
                btn = ev.value  # Get the hat value
            if btn is None:  # If btn is still None, continue to the next iteration
                continue
            else:
                self.thor.event = str(btn)  # Set the event in thor instance
            self.handle_button(btn)

    def handle_button(self, btn):
        match btn:  # Match the button value
            case 6:
                # Start a daemon thread to open the claw
                Thread(target=self.thor.open_claw, daemon=True).start()
            case 4:
                # Start a daemon thread to close the claw
                Thread(target=self.thor.close_claw, daemon=True).start()
            case (1, 0):
                # Start a daemon thread to rotate the claw
                Thread(target=self.thor.rotate_claw, daemon=True).start()
            case (-1, 0):
                # Start a daemon thread to rotate the claw clockwise
                Thread(target=self.thor.rotate_claw_cw, daemon=True).start()
            case (0, -1):
                # Start a daemon thread to move the claw backward
                Thread(target=self.thor.move_claw_b, daemon=True).start()
            case (0, 1):
                # Start a daemon thread to move the claw forward
                Thread(target=self.thor.move_claw, daemon=True).start()
            case 1:
                # Start a daemon thread to move articulation 4
                Thread(target=self.thor.art_4, daemon=True).start()
            case 3:
                # Start a daemon thread to move articulation 4 clockwise
                Thread(target=self.thor.art_4_cw, daemon=True).start()
            case 2:
                # Start a daemon thread to move articulation 3 backward
                Thread(target=self.thor.art_3_b, daemon=True).start()
            case 0:
                # Start a daemon thread to move articulation 3
                Thread(target=self.thor.art_3, daemon=True).start()
            case 5:
                # Start a daemon thread to move articulation 2 backward
                Thread(target=self.thor.art_2_b, daemon=True).start()
            case 7:
                # Start a daemon thread to move articulation 2
                Thread(target=self.thor.art_2, daemon=True).start()
            case 10:
                # Start a daemon thread to move articulation 1
                Thread(target=self.thor.art_1, daemon=True).start()
            case 11:
                # Start a daemon thread to move articulation 1 clockwise
                Thread(target=self.thor.art_1_cw, daemon=True).start()
            case 9:
                # Start a daemon thread to move to home position
                Thread(target=self.thor.home, daemon=True).start()


def main():
    controller = GamepadController()
    controller.run()


if __name__ == "__main__":
    main()
