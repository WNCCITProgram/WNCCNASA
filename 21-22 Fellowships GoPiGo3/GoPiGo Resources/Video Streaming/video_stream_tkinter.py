"""
    Name: video_streaming_tkinter.py
    Author: 
    Created: 09/08/22
    Purpose: Stream video to a Tkinter interface
"""
# sudo pip3 install opencv-python
# sudo pip3 install pillow -U
# sudo apt-get install libatlas-base-dev
# sudo pip3 install numpy -Y

import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
from PIL import Image
from PIL import ImageTk
import cv2


class VideoStar():
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Video Star OpenCV")
        self.root.minsize(width=640, height=20)
        # Call self.quit when window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        # Create numpy array to hold image data from cv2
        self.frame = np.random.randint(0, 255, [100, 100, 3], dtype='uint8')
        # Create img from numpy array
        self.img = ImageTk.PhotoImage(Image.fromarray(self.frame))

        self.create_widgets()
        self.root.mainloop()

    def display_video(self):
        # Create VideoCapture object 0 = 1st camera
        self.cam = cv2.VideoCapture(0)
        try:
            while True:
                # Read camera image frame by frame
                # ret = True or False
                # frame: captured image
                ret, self.frame = self.cam.read()
                # Convert cv2 colorspace BGR to RGB
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                # PIL Image.fromarray creates image from numpy array self.frame
                # ImageTk.PhotoImage converts image to Tkinter image format
                img_update = ImageTk.PhotoImage(Image.fromarray(self.frame))
                # Set label image to new image
                self.lbl_image.configure(image=img_update)
                self.lbl_image.image = img_update
                # Update the label to display the new image
                self.lbl_image.update()
                # self.display_fps()
                if not ret:
                    print("Failed to grab frame")
                    break

        except Exception as e:
            pass
            # print(f"{e}")

    def create_widgets(self):
        # Label to display video stream
        self.lbl_image = ttk.Label(self.root)

        message = f"OpenCV Video Stream"
        self.lbl_text = ttk.Label(self.root, text=message)

        btn_start = ttk.Button(
            self.root, text="Start", command=self.display_video, width=20)
        btn_stop = ttk.Button(
            self.root, text="Quit", command=self.quit, width=20)

        self.lbl_image.grid(row=0, column=0, columnspan=3)
        self.lbl_text.grid(row=1, column=1)
        btn_start.grid(row=1, column=0)
        btn_stop.grid(row=1, column=2)

        # Set padding for all widgets
        for child in self.root.winfo_children():
            child.grid_configure(padx=6, pady=6, ipadx=1, ipady=1)

    def display_fps(self):
        # Get and display FPS
        self.fps = self.cam.get(cv2.CAP_PROP_FPS)
        message = f"FPS: {self.fps}"
        self.lbl_text.configure(text=message)
        self.lbl_text.update()

    def quit(self):
        self.cam.release()
        cv2.destroyAllWindows()
        self.root.destroy()


video_star = VideoStar()
