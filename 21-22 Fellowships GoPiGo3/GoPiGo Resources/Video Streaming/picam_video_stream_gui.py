"""
    Filename: picam_video_stream_gui.py
    Use picamera 1.13 in Buster to stream video
"""

import tkinter as tk
import picamera
import picamera.array
# sudo pip3 install pillow -U
from PIL import Image, ImageTk


class VideoApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 24

        self.video_stream = picamera.array.PiRGBArray(
            self.camera, size=(640, 480)
        )
        self.streaming = False

        self.start_button = tk.Button(
            window, text="Start Stream", command=self.start_stream
        )
        self.start_button.pack()

        self.stop_button = tk.Button(
            window, text="Stop Stream", command=self.stop_stream, state=tk.DISABLED
        )
        self.stop_button.pack()

        self.capture_button = tk.Button(
            window, text="Capture Still", command=self.capture_still)
        self.capture_button.pack()

        self.canvas = tk.Canvas(
            window, width=self.camera.resolution[0], height=self.camera.resolution[1]
        )
        self.canvas.pack()

        self.update()
        self.window.mainloop()

    def start_stream(self):
        self.streaming = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_stream(self):
        self.streaming = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def capture_still(self):
        self.camera.capture('still_image.jpg')
        print("Still image captured.")

    def update(self):
        if self.streaming:
            self.camera.capture(self.video_stream, 'rgb')
            image = Image.fromarray(self.video_stream.array)
            self.photo = ImageTk.PhotoImage(image=image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.video_stream.seek(0)
            self.video_stream.truncate()
        self.window.after(10, self.update)

    def __del__(self):
        self.camera.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoApp(root, "Raspberry Pi Camera Stream")
