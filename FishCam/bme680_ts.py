#!/usr/bin/env python3
"""
Filename: bme680_ts.py
Description: BME680 sensor abstraction module
Provides temperature, humidity, and barometric pressure readings
from Bosch BME680 sensor connected via I2C bus
"""

# sudo pip3 install bme680
import bme680
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

# Pressure offset to match National Weather Service readings
# Aquaponics system in Scottsbluff, NE
# If the sensor reading is low, decrease
# If the sensor reading is high, increase
PRESSURE_OFFSET = 0.05

# Get logger for this module (no handlers configured here)
logger = logging.getLogger(__name__)


class BME680Sensor:
    """
    BME680 sensor wrapper class for aquaponics monitoring.
    Handles initialization, data reading, and calibration.
    """

    def __init__(self):
        """Initialize the BME680 sensor with I2C connection."""
        try:
            # Initialize sensor object, make connection to sensor over I2C
            self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
            logger.info("BME680 sensor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize BME680 sensor: {e}")
            raise

    def read_sensors(self):
        """
        Read temperature, humidity, and barometric pressure from BME680.

        Returns:
            tuple: (temp_f, humidity, pressure_inhg) or (None, None, None) if error
            - temp_f: Temperature in Fahrenheit
            - humidity: Relative humidity as percentage
            - pressure_inhg: Barometric pressure in inches of mercury
        """
        try:
            # Can the sensor data be retrieved successfully?
            if self.sensor.get_sensor_data():
                # Sensor output in celsius
                temp_c = self.sensor.data.temperature
                # Convert celsius to fahrenheit
                temp_f = ((temp_c * 9.0) / 5.0) + 32

                # Relative humidity in %
                humidity = self.sensor.data.humidity

                # Sensor output in hectoPascals (hPa), also called millibars
                pressure_pascals = self.sensor.data.pressure
                # Convert hPa hectopascals to inHg Inches of Mercury
                pressure_inhg = pressure_pascals / 33.863886666667
                # Compensate for 3960' altitude 4.04
                # Scottsbluff, NE, Heilig Field, 4.04
                pressure_inhg = pressure_inhg + 4.04

                # Pressure offset to match local weather station pressure
                pressure_inhg = pressure_inhg - PRESSURE_OFFSET

                return temp_f, humidity, pressure_inhg
            else:
                logger.warning("Failed to get BME680 sensor data")
                return None, None, None

        except Exception as e:
            logger.error(f"Error reading BME680 sensor: {e}")
            return None, None, None


# Convenience function for backwards compatibility
def read_bme680():
    """
    Convenience function to read BME680 sensor data.
    Creates a temporary sensor instance and returns readings.

    Returns:
        tuple: (temp_f, humidity, pressure_inhg) or (None, None, None) if error
    """
    try:
        sensor = BME680Sensor()
        return sensor.read_sensors()
    except Exception as e:
        logger.error(f"Failed to read BME680 sensor: {e}")
        return None, None, None


# Test function for standalone execution
def main():
    """Test function to verify BME680 sensor functionality."""
    print("Testing BME680 sensor...")

    try:
        sensor = BME680Sensor()
        temp_f, humidity, pressure_inhg = sensor.read_sensors()

        if temp_f is not None:
            print(f"Temperature: {temp_f:.1f} °F")
            print(f"Humidity: {humidity:.1f}%")
            print(f"Pressure: {pressure_inhg:.2f} inHg")
        else:
            print("Failed to read sensor data")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Configure file and console logging only when run directly
    log_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    # Create logs directory relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # File handler with daily rotation, keep 7 days
    log_file_path = os.path.join(logs_dir, "bme680_ts.log")
    file_handler = TimedRotatingFileHandler(
        log_file_path,
        when="midnight",
        interval=1,
        backupCount=7,
    )
    file_handler.setFormatter(log_formatter)
    # Add date to rotated log files
    file_handler.suffix = "%Y-%m-%d"

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)

    # Configure logging with our handlers
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Prevent propagation to avoid duplicate messages
    logger.propagate = False

    main()
