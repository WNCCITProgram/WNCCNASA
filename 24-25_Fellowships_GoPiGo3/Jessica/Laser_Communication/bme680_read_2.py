#!/usr/bin/env python3
"""
    Filename: bme680_read_2.py
   Purpose: Use Pimoroni library to read
    temperature, pressure, and humidity from Bosch bme680 sensor
    !Connect to I2C bus
    Press Ctrl+C to exit
"""
from sys import exit
from time import sleep

# sudo pip3 install bme680
import bme680

# Initialize sensor object, make connection to sensor over I2C
sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)

print(" BME680 Read temperature, pressure, and humidity")
print(" Press CTRL+C to Exit")

try:
    while True:
        # Can the sensor data can be retrieved successfully?
        if sensor.get_sensor_data():
            # If sensor data retrieval is successful,
            # retrieve and display the data

            # Sensor output in celsius
            temp_c = sensor.data.temperature

            # Relative humidity in %
            humidity = sensor.data.humidity

            # Sensor output in hectoPascals (hPa), also called millibars
            pressure_hpa = sensor.data.pressure

            print(f" {temp_c:.1f} C | {humidity:.0f} % | {
                  pressure_hpa:.2f} hPa")

            sleep(1)

except KeyboardInterrupt:
    print("Bye!")
    exit(0)
