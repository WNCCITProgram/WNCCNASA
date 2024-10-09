#!/usr/bin/python3
"""
    Name: picam2_video_1.py
    Author: ChatGPT (Adapted by William A Loring)
    Created: 07/22/24
    Purpose: Stream video to a Tkinter interface using Picamera2
    Raspberry Pi Bullseye and Bookworm
"""
# sudo pip3 install pillow -U
# Import PIL for image processing
from PIL import Image, ImageTk
import tkinter as tk
from picamera2 import Picamera2


class PiCameraApp:
    def __init__(self, root):
        """
        Initialize the PiCameraApp class.

        Args:
            root: The Tkinter root window.
        """
        self.root = root  # Store the root window
        self.root.title("PiCamera2 Video Display")  # Set the window title

        # Initialize the Picamera2 object
        self.picam2 = Picamera2()

        # ---------- CONFIGURE CAMERA SETTINGS --------------------------- #
        # Set resolution to 640x480
        self.picam2.preview_configuration.main.size = (
            640, 480)
        # Set the frame rate to 30 FPS
        self.picam2.preview_configuration.controls.FrameRate = 30
        # Align the requested size with a standard video mode
        self.picam2.preview_configuration.align()
        # Apply the configuration settings
        self.picam2.configure("preview")

        # Start the camera
        self.picam2.start()

        # Create a Label widget to display the video frames
        self.label = tk.Label(root)
        # Add the Label widget to the window
        self.label.pack()

        # Start updating the image on the Label widget
        self.update_image()

# -------------------------- UPDATE IMAGE -------------------------------- #
    def update_image(self):
        """
        Capture an image from the camera and update the Label widget
        with the new image.
        """
        # Capture a frame from the camera as an array
        frame = self.picam2.capture_array()

        # Convert the frame array to an image that
        # can be displayed in Tkinter
        image = Image.fromarray(frame)
        image = ImageTk.PhotoImage(image)

        # Update the Label widget with the new image
        self.label.config(image=image)
        self.label.image = image

        # Schedule the update_image method to be called again
        # after 10 milliseconds
        self.root.after(10, self.update_image)


# The main block of the script
if __name__ == "__main__":
    # Create the Tkinter root window
    root = tk.Tk()

    # Create an instance of the PiCameraApp class
    app = PiCameraApp(root)

    # Start the Tkinter main loop
    root.mainloop()
