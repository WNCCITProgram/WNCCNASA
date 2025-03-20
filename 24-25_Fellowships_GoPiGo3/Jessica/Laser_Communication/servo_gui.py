import tkinter as tk
from tkinter import ttk
from time import sleep
import easygopigo3 as easy


class ServoControllerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GoPiGo Servo Controller")

        # Add padding around the main window
        self.root.configure(padx=10, pady=10)

        # Constants for servo movement
        self.MOVE = 5
        self.FORWARD = 90

        # Initialize GoPiGo and servos
        self.gpg = easy.EasyGoPiGo3()
        self.servo1 = self.gpg.init_servo("SERVO1")
        self.servo2 = self.gpg.init_servo("SERVO2")

        # Initialize servo positions
        self.servo1_pos = 90
        self.servo2_pos = 90

        self.setup_gui()
        self.update_displays()

        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_gui(self):
        # Create main frames
        self.create_servo1_section()
        self.create_servo2_section()

        # Bind keyboard events
        self.root.bind('<q>', lambda e: self.servo1_up())
        self.root.bind('<w>', lambda e: self.servo1_center())
        self.root.bind('<e>', lambda e: self.servo1_down())
        self.root.bind('<a>', lambda e: self.servo2_left())
        self.root.bind('<s>', lambda e: self.servo2_center())
        self.root.bind('<d>', lambda e: self.servo2_right())
        # Close window with Escape key
        self.root.bind('<Escape>', lambda e: self.on_closing())

    def create_servo1_section(self):
        # Servo 1 Frame
        servo1_frame = ttk.LabelFrame(
            self.root, text="Servo 1 Vertical", padding=10)
        servo1_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # Servo 1 Controls

        ttk.Button(servo1_frame, text="Up (Q)", command=self.servo1_up).grid(
            row=1, column=0, padx=5, pady=5)
        ttk.Button(servo1_frame, text="Center (W)", command=self.servo1_center).grid(
            row=1, column=1, padx=5, pady=5)
        ttk.Button(servo1_frame, text="Down (E)", command=self.servo1_down).grid(
            row=1, column=2, padx=5, pady=5)

        self.servo1_label = ttk.Label(servo1_frame, text="Position: 90°",
                                      font=('Helvetica', 10))
        self.servo1_label.grid(row=2, column=0, columnspan=3, pady=(10, 0))

    def create_servo2_section(self):
        # Servo 2 Frame
        servo2_frame = ttk.LabelFrame(
            self.root, text="Servo 2 Horizontal", padding=10)
        servo2_frame.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")

        ttk.Button(servo2_frame, text="Left (A)", command=self.servo2_left).grid(
            row=1, column=0, padx=5, pady=5)
        ttk.Button(servo2_frame, text="Center (S)", command=self.servo2_center).grid(
            row=1, column=1, padx=5, pady=5)
        ttk.Button(servo2_frame, text="Right (D)", command=self.servo2_right).grid(
            row=1, column=2, padx=5, pady=5)

        self.servo2_label = ttk.Label(servo2_frame, text="Position: 90°",
                                      font=('Helvetica', 10))
        self.servo2_label.grid(row=2, column=0, columnspan=3, pady=(10, 0))

    def update_displays(self):
        """Update the position labels for both servos"""
        self.servo1_label.config(text=f"Position: {self.servo1_pos}°")
        self.servo2_label.config(text=f"Position: {self.servo2_pos}°")

    def move_servo(self, servo_num, position):
        """Move the specified servo to the given position"""
        # Ensure position is within valid range
        position = min(180, max(0, position))

        # Update position and move servo
        if servo_num == 1:
            self.servo1_pos = position
            self.servo1.rotate_servo(position)
        else:
            self.servo2_pos = position
            self.servo2.rotate_servo(position)

        self.update_displays()
        sleep(0.1)

    # Servo 1 control methods
    def servo1_up(self):
        self.move_servo(1, self.servo1_pos - self.MOVE)

    def servo1_down(self):
        self.move_servo(1, self.servo1_pos + self.MOVE)

    def servo1_center(self):
        self.move_servo(1, self.FORWARD)

    # Servo 2 control methods
    def servo2_left(self):
        self.move_servo(2, self.servo2_pos + self.MOVE)

    def servo2_right(self):
        self.move_servo(2, self.servo2_pos - self.MOVE)

    def servo2_center(self):
        self.move_servo(2, self.FORWARD)

    def on_closing(self):
        """Clean up when the window is closed"""
        print("\nClosing program and resetting servos...")
        self.servo1.disable_servo()
        self.servo2.disable_servo()
        self.gpg.reset_all()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ServoControllerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
