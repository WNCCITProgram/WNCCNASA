#!/usr/bin/env python3
"""
    Name: thingspeak_distance_sensor.py
    Author: Wiiliam A Loring
    Created? 10/17/21 Revised:
    Purpose: Example of uploading data to a Thingspeak Channel
"""
# This uses the EasyGoPiGo3 library
# https://gopigo3.readthedocs.io/en/master/api-basic/easygopigo3.html#easygopigo3

# Import the time library for the sleep function
import requests
from time import sleep
from di_sensors.easy_temp_hum_press import EasyTHPSensor
from easygopigo3 import EasyGoPiGo3     # Import GoPiGo3 library

# Substitute your api key in this file for updating your ThingSpeak channel
import thingspeak_temp_api_key
TS_KEY = thingspeak_temp_api_key.THINGSPEAK_API_KEY

# ThingSpeak data dictionary
ts_data = {}    # Thingspeak data dictionary

# Create an instance of the GoPiGo3 class
gpg = EasyGoPiGo3()

# Initialize a Distance Sensor object
my_distance_sensor = gpg.init_distance_sensor()

# Initialize an EasyTHPSensor object
my_thp = EasyTHPSensor()

def main():
    try:
        while True:
            # Read temperature
            # temp = my_thp.safe_celsius()
            temp = my_thp.safe_fahrenheit()

            # Read relative humidity
            hum = my_thp.safe_humidity()

            # Read pressure in pascals
            press = my_thp.safe_pressure()

            # Convert pascals to inHg, compensate for 4000' altitude
            press = (press / 3386.38867) + 4.08

            # Print values to the console
            print("Temperature: {:5.1f}F  Humidity: {:5.1f}%  Pressure: {:5.2f} inHg".format(
                temp, hum, press))

             # Send sensor data to ThingSpeak
            thingspeak_send(temp, hum, press)

            # Pause between readings
            sleep(5)
    # Except the program gets interrupted by Ctrl+C on the keyboard
    except KeyboardInterrupt:
        # Unconfigure the sensors, disable the motors,
        # and restore the LED to the control of the GoPiGo3 firmware
        gpg.reset_all()

def thingspeak_send(temp, hum, press):
    """
        Update the ThingSpeak channel using the requests library
    """
    print("Update ThingSpeak Channel")

    # Each field number corresponds to a field in ThingSpeak
    params = {
        "api_key": TS_KEY,
        "field1": temp,
        "field2": hum,
        "field3": press
    }

    # Update data on Thingspeak
    ts_update = requests.get(
        "https://api.thingspeak.com/update", params=params)

    # Was the update successful?
    if ts_update.status_code == requests.codes.ok:
        print("Data Received!")
    else:
        print("Error Code: " + str(ts_update.status_code))

    # Print ThingSpeak response to console
    # ts_update.txt is the thingspeak data entry number in the channel
    print("ThingSpeak Channel Entry: " + ts_update.text)

# If a standalone program, call the main function
# Else, use as a module
if __name__ == '__main__':
    main()