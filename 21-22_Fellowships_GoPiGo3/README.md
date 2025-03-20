# WNCC NASA NeSpaceGrant.org
- These projects are supported by the Nebraska SpaceGrant https://www.nespacegrant.org
- This is the pespository for Western Nebraska Community College NASA Nebraska Space Grant Student Fellowships
- This is part of an ongoing project sponsored by the Nebraska Space Grant
  - Enhancing Computer Science Curriculum using off-the-shelf Robotics Kits to Increase Whole Brain Learning

# NASA Fellowships 21-22 GoPiGo3
- All Python code is Python3 compatible with Python 3.7.3 on the GoPiGo3 with Buster
## Equipment
- GoPiGo3 from Modular Robotics https://gopigo.io
- Sensors from Modular Robotics and Grove
- Raspberry Pi OS Buster, GoPiGo3 libraries
## Resources
- GoPiGo3 Getting Started Buster (Start here)
- GoPiGo3 Tutorials and Resources
- GoPiGo3 Cloud Data with ThingSpeak Tutorial (Using the Distance Sensor)
- GoPiGo3 Scratch for Robots Tutorial
- GoPiGo3 library documentation
  - https://gopigo3.readthedocs.io/en/latest
  - https://di-sensors.readthedocs.io/en/latest
- Programming Resources (General programming resources)
- Video Streaming --> Folder with tutorials and programs that use the Python OpenCV-Python library to take stills and stream video
### Resources --> Code Examples --> Sensors Folder contains sensor tutorial and code
- GoPiGo3 Sensors Tutorial
- sensor_distance_test.py --> Read the Dexter distance sensor in inches and mm to the console
- sensor_imu_test.py --> Read Dexter IMU sensor (magnetometer, gyroscope, accelerometer, euler, and temperature)
- sensor_ir_test.py --> Dexter IR sensor reads the GoPiGo IR remote control
- sensor_light_color_test.py --> Dexter Light Color Sensor
### Resources --> Code Examples (Python 3.7.3)
- Original program code from:
  - GoPiGo3 file system, /Dexter/Software/Python/Examples/ or
  - https://github.com/DexterInd/GoPiGo3
- blinkers.py --> Turn the blinkers on the front on and off
- buzzer.py --> Play notes on the piezo buzzer
- dead_reckoning_movement.py --> Dead reckoning movement using various GoPiGo movement methods
- dex_eyes.py --> Turn the led's on the top (robot eyes) to different colors
- distance_sensor.py --> Test the distance sensor
- gopigo_info.py --> GoPiGo system information
- obstacle_avoidance.py --> Obstacle avoidance with distance sensor
- polyangle_console.py --> Calculate the interior and exterior angles of a regular polygon
- pygame_timer_countdown.py --> Example of using a pygame timer event, concept can be used to read sensors in rc_pygame.py
- rc_console.py --> Console remote control
- rc_obstacle_avoidance_console.py --> Multithreaded console remote control and obstacle avoidance
- rc_obstacle_avoidance_pygame.py --> Pygame GUI remote control and obstacle avoidance
- rc_obstacle_avoidance_tkinter.py --> Tkinter GUI remote control and obstacle avoidance
- rc_pygame.py --> PyGame GUI remote control
- rc_tkinter.py --> Tkinter GUI remote control, battery voltage display
- servo.py --> Test the servo
- startup_mailer.py --> Email the IP address of the local device on startup
#### Run all Python programs at the console --> python3 filename.py
#### GoPiGo3 ThingSpeak example logging: http://www.billthecomputerguy.com/gopigo 
### License
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.
