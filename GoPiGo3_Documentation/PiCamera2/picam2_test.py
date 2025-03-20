""" 
---------------------------------------------------------------
# Filename: picam2_test.py
# Author:   William A Loring
# Created:  10/17/21
# Purpose:  Test Picamera2 library with Pi Camera on MARSROVER
 Original script: https://raspberrytips.com/picamera2-raspberry-pi/
 ---------------------------------------------------------------
Users of Raspberry Pi 3 or earlier devices will need to enable Glamor
for this example script using XWindows to work. To do this,
run sudo raspi-config in a command window, choose Advanced Options and then
enable Glamor graphic acceleration. Finally reboot your device.
 """

import time
# To test: libcamera_hello
import libcamera
# Import the PiCamera library
from picamera2 import Picamera2, Preview
# Initialize a Picamera2 object
picam = Picamera2()

# Create camera_config object
# lores is for preview before taking the picture
# main is the still image resolution
config = picam.create_still_configuration(
    main={"size": (1920, 1080)},
    lores={"size": (640, 480)},
    display="lores"
)
# config["transform"] = libcamera.Transform(hflip=1, vflip=1)
# Load the configuration
picam.configure(config)
# Start preview window
picam.start_preview(Preview.QTGL)
# Start the camera
picam.start()
time.sleep(2)
# Capture image
picam.capture_file("test.jpg")
