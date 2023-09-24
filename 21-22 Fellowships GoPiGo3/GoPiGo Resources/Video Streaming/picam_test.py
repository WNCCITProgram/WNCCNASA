""" 
    Filename: picam_test.py
    Author:   William A Loring
    Created:  07/30/23
    Purpose:  Test PiCamera library with Pi Camera
    Using Pi OS Buster and picamera 1.13
    picamera 1.13 is preinstalled in Buster
"""
from time import sleep
from picamera import PiCamera

# Create camera object
camera = PiCamera()

# Set camera resolution in pixels
camera.resolution = (1024, 768)

# Start camera
camera.start_preview()

# Camera warm-up time
sleep(2)
# Capture and save foo.jpg in current folder
camera.capture('foo.jpg')
