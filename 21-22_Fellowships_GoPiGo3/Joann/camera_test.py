# ---------------------------------------------------------
# Filename: camera_test.py
# Author: 
# Created:
# Pupose: Test PiCamera
# Original program from RaspberryPi.org
# --------------------------------------------------------

from picamera import PiCamera   # Import the PiCamera library
from time import sleep          # Import sleep

camera = PiCamera()             # Initialize a PiCamera object

# You won't see the preview through VNC
# The preview is needed to warm up the camera
print("Warming up camera")
camera.start_preview()
# The preview is neede to warm up the camera and sense light levels
sleep (2)

# Capture the image to a file
print("Capture the image")
camera.capture('/home/pi/Desktop/picamera_test.jpg')

# Shutdown the camera
print("Shut down the camera")
camera.stop_preview()