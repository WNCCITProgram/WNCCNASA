#!/usr/bin/python3
"""
    Name: picam2_video_2.py
    Author: ChatGPT (Adapted by William A Loring)
    Created: 07/22/24
    Purpose: Stream video to a Tkinter interface using Picamera2
    Raspberry Pi Bullseye and Bookworm
"""

import tkinter as tk  # Import the tkinter library for creating the GUI
# Import the Label and Button widgets from tkinter
from tkinter import Label, Button
# Import Picamera2 for controlling the camera
from picamera2 import Picamera2, Preview
from PIL import Image, ImageTk  # Import PIL for image processing

# Define a class to encapsulate the camera and Tkinter functionality


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

        # Create a preview configuration for the camera
        self.config = self.picam2.create_preview_configuration()

        # Configure the camera with the preview configuration
        self.picam2.configure(self.config)

        # Create a Label widget to display the video frames
        self.label = Label(root)
        self.label.pack()  # Add the Label widget to the window

        # Create a Start button to start the video stream
        self.start_button = Button(
            root, text="Start", command=self.start_stream)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Create a Stop button to stop the video stream
        self.stop_button = Button(root, text="Stop", command=self.stop_stream)
        self.stop_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.streaming = False  # A flag to control the streaming state

    def start_stream(self):
        """
        Start the video stream.
        """
        self.streaming = True  # Set the streaming flag to True
        self.update_image()  # Start updating the image

    def stop_stream(self):
        """
        Stop the video stream.
        """
        self.streaming = False  # Set the streaming flag to False

    def update_image(self):
        """
        Capture an image from the camera and update the Label widget with the new image.
        """
        if self.streaming:  # Check if streaming is enabled
            # Capture a frame from the camera as an array
            frame = self.picam2.capture_array()

            # Convert the frame array to an image that can be displayed in Tkinter
            image = Image.fromarray(frame)
            image = ImageTk.PhotoImage(image)

            # Update the Label widget with the new image
            self.label.config(image=image)
            self.label.image = image

            # Schedule the update_image method to be called again after 10 milliseconds
            self.root.after(10, self.update_image)


# The main block of the script
if __name__ == "__main__":
    # Create the Tkinter root window
    root = tk.Tk()

    # Create an instance of the PiCameraApp class
    app = PiCameraApp(root)

    # Start the Tkinter main loop
    root.mainloop()
