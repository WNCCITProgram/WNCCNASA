#!/usr/bin/python3
"""
    Name: video_star.py
    Author: 
    Created: 08/01/23
    Purpose: Stream video to a Tkinter interface using opencv
"""

import tkinter as tk  # Import the tkinter library for creating the GUI
from tkinter import Label, Button  # Import the Label and Button widgets from tkinter
from picamera2 import Picamera2  # Import Picamera2 for controlling the camera
from PIL import Image, ImageTk  # Import PIL for image processing
import datetime  # Import datetime for timestamping the saved images
import threading  # Import threading for running capture in a separate thread
import time  # Import time for timing FPS calculation

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

        # Create a Label widget to display the FPS
        self.fps_label = Label(root, text="FPS: 0")
        self.fps_label.pack(side=tk.BOTTOM, pady=10)

        # Create a Start button to start the video stream
        self.start_button = Button(root, text="Start", command=self.start_stream)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Create a Stop button to stop the video stream
        self.stop_button = Button(root, text="Stop", command=self.stop_stream)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Create a Capture button to capture a still image
        self.capture_button = Button(root, text="Capture", command=self.capture_image)
        self.capture_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.streaming = False  # A flag to control the streaming state
        self.frame_count = 0  # Counter for the number of frames
        self.start_time = time.time()  # Start time for FPS calculation
        self.frame_interval = 1000 / 30  # Frame interval in milliseconds (for 30 FPS)
        self.image = None  # Store the latest image

        # Initialize and start the capture thread
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.capture_thread.daemon = True  # Allow the thread to exit when the main program exits
        self.capture_thread.start()

    def start_stream(self):
        """
        Start the video stream.
        """
        self.streaming = True  # Set the streaming flag to True
        self.picam2.start()  # Start the camera
        self.update_image()  # Start updating the image

    def stop_stream(self):
        """
        Stop the video stream.
        """
        self.streaming = False  # Set the streaming flag to False
        self.picam2.stop()  # Stop the camera

    def capture_image(self):
        """
        Capture a still image in a separate thread and save it to the hard drive.
        """
        if not self.streaming:  # Ensure that streaming is stopped before capturing
            threading.Thread(target=self._capture_image_thread).start()

    def _capture_image_thread(self):
        """
        The actual method that captures the image and saves it to the hard drive.
        This is run in a separate thread to prevent blocking the main thread.
        """
        if not self.streaming:  # Check again if streaming is stopped
            if self.image is not None:
                # Convert the frame array to an image
                image = Image.fromarray(self.image)

                # Convert image to RGB mode if necessary
                if image.mode == 'RGBA':
                    image = image.convert('RGB')

                # Generate a timestamped filename for the image
                filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
                image.save(filename, 'JPEG')  # Save the image to the hard drive in JPEG format
                print(f"Image saved as {filename}")

    def _capture_frames(self):
        """
        Continuously capture frames from the camera in a separate thread.
        """
        while True:
            if self.streaming:
                frame = self.picam2.capture_array()  # Capture a frame from the camera
                self.image = frame  # Store the latest frame
                time.sleep(self.frame_interval / 1000.0)  # Sleep to maintain frame interval

    def update_image(self):
        """
        Update the Label widget with the latest image from the camera.
        """
        if self.image is not None:  # Check if there is a frame to display
            # Convert the frame array to an image that can be displayed in Tkinter
            image = Image.fromarray(self.image)
            image = ImageTk.PhotoImage(image)

            # Update the Label widget with the new image
            self.label.config(image=image)
            self.label.image = image

            # Calculate FPS every second
            self.frame_count += 1
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            if elapsed_time > 1.0:
                fps = self.frame_count / elapsed_time
                self.fps_label.config(text=f"FPS: {fps:.2f}")
                self.frame_count = 0
                self.start_time = current_time

        # Schedule the update_image method to be called again
        self.root.after(int(self.frame_interval), self.update_image)

# The main block of the script
if __name__ == "__main__":
    # Create the Tkinter root window
    root = tk.Tk()

    # Create an instance of the PiCameraApp class
    app = PiCameraApp(root)

    # Start the Tkinter main loop
    root.mainloop()
