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
import time
import requests
from easygopigo3 import EasyGoPiGo3     # Import GoPiGo3 library

# Substitute your api key in this file for updating your ThingSpeak channel
import thingspeak_api_key
TS_KEY = thingspeak_api_key.THINGSPEAK_API_KEY

# ThingSpeak data dictionary
ts_data = {}    # Thingspeak data dictionary

# Create an instance of the GoPiGo3 class
gpg = EasyGoPiGo3()

# Initialize a Distance Sensor object
my_distance_sensor = gpg.init_distance_sensor()

def main():
    while True:
        # ========================================================================
        # field1: Read the distance sensor data into millimeters
        mm = str(my_distance_sensor.read_mm())

        # ========================================================================
        # field2: Read the distance sensor data into inches
        inches = str(my_distance_sensor.read_inches())

        # Print the value of the sensor to the console for debugging
        print("Distance Sensor Reading: " + inches + " inches " + mm + " mm")

        # Send sensor data to ThingSpeak
        thingspeak_send(mm, inches)

        # 15 seconds is the minimum amount of time between uploads
        # Sleep is set to 15 seconds for testing purposes
        time.sleep(15)

def thingspeak_send(mm, inches):
    """
        Update the ThingSpeak channel using the requests library
    """
    print("Update ThingSpeak Channel")

    # Each field number corresponds to a field in ThingSpeak
    params = {
        "api_key": TS_KEY,
        "field1": mm,
        "field2": inches
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