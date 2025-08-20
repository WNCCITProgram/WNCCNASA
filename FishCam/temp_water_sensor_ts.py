#!/usr/bin/env python3
"""
Filename: temp_water_sensor_ts.py
Description: Water temperature sensor abstraction module
Provides water temperature readings from DS18B20 sensor
connected via 1-Wire interface
"""

import logging
import os
import sys
import time
from logging.handlers import TimedRotatingFileHandler

# pip install w1thermsensor
from w1thermsensor import W1ThermSensor

# Get logger for this module (no handlers configured here)
logger = logging.getLogger(__name__)


class WaterTemperatureSensor:
    """
    Water temperature sensor wrapper class for aquaponics monitoring.
    Handles DS18B20 1-Wire temperature sensor initialization and data reading.
    """

    def __init__(self):
        """Initialize the DS18B20 water temperature sensor with 1-Wire connection."""
        try:
            # Create an instance of the W1ThermSensor
            self.sensor = W1ThermSensor()
            logger.info("DS18B20 water temperature sensor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DS18B20 water temperature sensor: {e}")
            raise

    def read_temperature(self):
        """
        Read water temperature from DS18B20 sensor.

        Returns:
            float: Temperature in Celsius, or None if error
        """
        try:
            temperature = self.sensor.get_temperature()
            logger.debug(f"Water temperature reading: {temperature:.2f}°C")
            return temperature
        except Exception as e:
            logger.error(f"Error reading water temperature: {e}")
            return None

    def read_temperature_fahrenheit(self):
        """
        Read water temperature from DS18B20 sensor and convert to Fahrenheit.

        Returns:
            float: Temperature in Fahrenheit, or None if error
        """
        temp_c = self.read_temperature()
        if temp_c is not None:
            temp_f = (temp_c * 9 / 5) + 32
            logger.debug(f"Water temperature reading: {temp_f:.2f}°F")
            return temp_f
        return None

    def get_temperature_status(self):
        """
        Get water temperature with status information.

        Returns:
            tuple: (temperature_c, status_string) where:
            - temperature_c: Temperature in Celsius or None if error
            - status_string: Human-readable status description
        """
        temp_c = self.read_temperature()
        if temp_c is not None:
            temp_f = (temp_c * 9 / 5) + 32
            status = f"Water Temperature: {temp_f:.1f}°F ({temp_c:.1f}°C)"
            return temp_c, status
        else:
            return None, "Water Temperature: Sensor Error"


# Convenience function for backwards compatibility
def read_temperature():
    """
    Convenience function to read water temperature sensor data.
    Creates a temporary sensor instance and returns readings in Celsius.

    Returns:
        float: Temperature in Celsius, or None if error
    """
    try:
        sensor = WaterTemperatureSensor()
        return sensor.read_temperature()
    except Exception as e:
        logger.error(f"Failed to read water temperature sensor: {e}")
        return None


def read_temperature_fahrenheit():
    """
    Convenience function to read water temperature sensor data in Fahrenheit.
    Creates a temporary sensor instance and returns readings in Fahrenheit.

    Returns:
        float: Temperature in Fahrenheit, or None if error
    """
    try:
        sensor = WaterTemperatureSensor()
        return sensor.read_temperature_fahrenheit()
    except Exception as e:
        logger.error(f"Failed to read water temperature sensor: {e}")
        return None


# Test function for standalone execution
def main():
    """Test function to verify water temperature sensor functionality."""
    print("Testing DS18B20 water temperature sensor...")

    try:
        sensor = WaterTemperatureSensor()
        
        print("Reading water temperature every 5 seconds...")
        print("Press Ctrl+C to exit")
        
        while True:
            temp_c = sensor.read_temperature()
            
            if temp_c is not None:
                temp_f = (temp_c * 9 / 5) + 32
                print(f"Water Temperature: {temp_f:.2f}°F ({temp_c:.2f}°C)")
            else:
                print("Failed to read water temperature")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nExiting...")
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
    log_file_path = os.path.join(logs_dir, "temp_water_sensor_ts.log")
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
