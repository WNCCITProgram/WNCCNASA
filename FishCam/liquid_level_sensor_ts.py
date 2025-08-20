#!/usr/bin/env python3
"""
Filename: liquid_level_sensor_ts.py
Description: Liquid level sensor abstraction module
Provides liquid level detection for aquaponics monitoring system
Standalone implementation using GPIO Zero for direct sensor access
"""

import logging
import os
import sys
import time
from logging.handlers import TimedRotatingFileHandler

# Import GPIO Zero for direct sensor control

try:
    from gpiozero import DigitalInputDevice

    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

# Define the GPIO pin number where the sensor is connected
SENSOR_PIN = 18  # GPIO pin 18 (physical pin 12)

# Get logger for this module (no handlers configured here)
logger = logging.getLogger(__name__)


class LiquidLevelSensor:
    """
    Liquid level sensor wrapper class for aquaponics monitoring.
    Handles initialization, data reading, and status reporting.
    Uses GPIO Zero for direct sensor control.
    """

    def __init__(self):
        """Initialize the liquid level sensor with GPIO Zero."""
        try:
            if not GPIO_AVAILABLE:
                raise ImportError("GPIO Zero library not available")

            # Create a DigitalInputDevice for the sensor
            # pull_up=False means we use a pull-down resistor (default behavior)
            # This ensures the pin reads False when no signal is present
            self.sensor = DigitalInputDevice(SENSOR_PIN, pull_up=False)
            logger.info(
                f"Liquid level sensor initialized on GPIO pin {SENSOR_PIN}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize liquid level sensor: {e}")
            self.sensor = None
            raise

    def read_sensor(self):
        """
        Read liquid level sensor status using GPIO Zero.

        Returns:
            int: 1 if liquid detected, 0 if no liquid detected, None if error

        Note: Many liquid level sensors have inverted logic:
        - Sensor reads HIGH (True) when NO liquid is present
        - Sensor reads LOW (False) when liquid IS present
        So we invert the reading with 'not sensor.value'
        """
        try:
            if self.sensor is None:
                logger.error("Sensor not initialized")
                return None

            # GPIO Zero makes reading very simple - just check the 'value' property
            # We use 'not sensor.value' to invert the logic for sensors that read HIGH when dry
            liquid_present = not self.sensor.value

            if liquid_present:
                return 1  # Liquid detected
            else:
                return 0  # No liquid detected

        except Exception as e:
            logger.error(f"Error reading liquid level sensor: {e}")
            return None

    def get_status_string(self):
        """
        Get human-readable status string.

        Returns:
            str: Status description or error message
        """
        try:
            status = self.read_sensor()
            if status == 1:
                return "Liquid detected"
            elif status == 0:
                return "No liquid detected"
            else:
                return "Sensor error"
        except Exception as e:
            logger.error(f"Error getting liquid level status: {e}")
            return "Sensor error"

    def close(self):
        """Clean up GPIO resources."""
        try:
            if self.sensor:
                self.sensor.close()
                logger.info("Liquid level sensor GPIO resources cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up liquid level sensor: {e}")

    def __del__(self):
        """Destructor to ensure cleanup when object is destroyed."""
        self.close()


# Convenience function for backwards compatibility
def read_liquid_level():
    """
    Convenience function to read liquid level sensor.
    Creates a temporary sensor instance and returns reading.

    Returns:
        int: 1 if liquid detected, 0 if no liquid detected, None if error
    """
    try:
        sensor = LiquidLevelSensor()
        return sensor.read_sensor()
    except Exception as e:
        logger.error(f"Failed to read liquid level sensor: {e}")
        return None


# Test function for standalone execution
def main():
    """Test function to verify liquid level sensor functionality with continuous monitoring."""
    print("Testing liquid level sensor...")
    print(f"Monitoring GPIO pin {SENSOR_PIN} for liquid level changes")
    print("Press Ctrl+C to exit\n")

    sensor = None
    try:
        sensor = LiquidLevelSensor()

        while True:
            status = sensor.read_sensor()
            status_string = sensor.get_status_string()
            current_time = time.strftime("%H:%M:%S")

            if status is not None:
                if status == 1:
                    print(f"[{current_time}] ✓ {status_string}")
                else:
                    print(f"[{current_time}] ✗ {status_string}")
            else:
                print(f"[{current_time}] ⚠ Failed to read sensor data")

            # Wait 1 second before next reading
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if sensor:
            sensor.close()
        print("Sensor cleanup complete.")
        print("Program terminated.")


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
    log_file_path = os.path.join(logs_dir, "liquid_level_sensor_ts.log")
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
