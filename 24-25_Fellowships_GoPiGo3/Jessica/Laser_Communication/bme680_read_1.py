#!/usr/bin/env python3
"""
    Filename: bme680_read_1.py
    Purpose: Use Pimoroni library to read
    temperature, pressure, and humidity from Bosch bme680 sensor
    !Connect to I2C bus
    Press Ctrl+C to exit
"""
from time import sleep

# sudo pip3 install bme680
import bme680

# Initialize sensor object, make connection to sensor over I2C
sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)

print(" BME680 Read temperature, pressure, and humidity")
print(" Ctrl+C to exit!")

while True:
    # Read the sensor
    sensor.get_sensor_data()

    # Temperature in celsius
    print(sensor.data.temperature)

    # Barometric ressure in hPa (hectopascal)
    print(sensor.data.pressure)

    # Relative humidity in %
    print(sensor.data.humidity)

    sleep(1)
