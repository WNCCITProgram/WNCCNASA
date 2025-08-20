#!/usr/bin/env python3
"""
Filename: sensors_ts.py
Description: Display temperature, pressure, and humidity
from Bosch bme680 sensor with integrated email notifications
!Connect to I2C bus
Press Ctrl+C to exit
"""
import api_key_ts
import logging
import sys
import os
import re
from datetime import datetime
from time import sleep

# pip install requests
import requests

# pip install bme680
from bme680_ts import BME680Sensor
from liquid_level_sensor_ts import LiquidLevelSensor
from temp_water_sensor_ts import WaterTemperatureSensor
from ph_sensor_ts import PHSensor

# Import email notification system
from email_notification import EmailNotifier

# Import configuration constants
from aquaponics_config import (
    SENSOR_READ_INTERVAL,
    THINGSPEAK_INTERVAL,
    READINGS_PER_CYCLE,
    ENABLE_SCHEDULED_EMAILS,
    DAILY_EMAIL_TIME,
    DEFAULT_RECIPIENT_EMAILS,
)

# Configure logging
from logging.handlers import TimedRotatingFileHandler

# Create a module-specific logger to prevent conflicts
logger = logging.getLogger(__name__)

# Only configure if not already configured to prevent duplicates
if not logger.handlers:
    log_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    # Create logs directory relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # File handler with daily rotation, keep 7 days
    log_file_path = os.path.join(logs_dir, "sensors_ts.log")
    file_handler = TimedRotatingFileHandler(
        log_file_path,
        when="midnight",
        interval=1,
        backupCount=7,
    )
    file_handler.setFormatter(log_formatter)
    # Add date before .log extension for rotated files: sensors_ts.YYYY-MM-DD.log
    file_handler.suffix = ".%Y-%m-%d.log"
    file_handler.extMatch = re.compile(r"^\.\d{4}-\d{2}-\d{2}\.log$")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)

    # Configure logging with our handlers
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Prevent propagation to avoid duplicate messages
    logger.propagate = False

# Initialize sensor objects
sensor = BME680Sensor()
liquid_level_sensor = LiquidLevelSensor()
water_temp_sensor = WaterTemperatureSensor()
ph_sensor = PHSensor()

# Initialize email notification system
email_notifier = EmailNotifier()

# Substitute your api key in this file for updating your ThingSpeak channel
TS_KEY = api_key_ts.THINGSPEAK_API_KEY

# Global variables for email scheduling and water level tracking
last_daily_email_date = None
previous_water_level = None

# Create ThingSpeak data dictionary
ts_data = {}

logger.info("Aquaponics sensors send to ThingSpeak with email notifications")
logger.info(f"Reading sensors every {SENSOR_READ_INTERVAL} seconds")
logger.info(
    f"Averaging {READINGS_PER_CYCLE} readings over {THINGSPEAK_INTERVAL/60:.0f} minutes"
)
if ENABLE_SCHEDULED_EMAILS:
    logger.info(f"Daily summary emails at {DAILY_EMAIL_TIME}")
    logger.info("Water level change alerts enabled")
logger.info("Ctrl+C to exit!")


# ------------------------ CALCULATE TRIMMED MEAN -------------------------- #
def calculate_trimmed_mean(readings, trim_percent=0.1):
    """
    Calculate trimmed mean by removing outliers from the dataset.
    Removes trim_percent from both ends of the sorted data.
    Default removes 10% from each end (20% total).
    """
    if not readings:
        return 0.0

    if len(readings) == 1:
        return readings[0]

    # Sort the readings
    sorted_readings = sorted(readings)

    # Calculate number of values to trim from each end
    trim_count = max(1, int(len(sorted_readings) * trim_percent))

    # Ensure we don't trim all values
    if trim_count * 2 >= len(sorted_readings):
        trim_count = 0

    # Remove outliers from both ends
    if trim_count > 0:
        trimmed_readings = sorted_readings[trim_count:-trim_count]
    else:
        trimmed_readings = sorted_readings

    # Calculate and return the mean
    return sum(trimmed_readings) / len(trimmed_readings)


# ---------------- GET CURRENT SENSOR DATA FOR EMAIL ----------------------- #
def get_current_sensor_data_for_email(
    temp_f, humidity, pressure_inhg, water_temp_f, liquid_present, ph_value=None
):
    """
    Format current sensor readings for email reports.

    Args:
        temp_f: Air temperature in Fahrenheit
        humidity: Humidity percentage
        pressure_inhg: Pressure in inches of mercury
        water_temp_f: Water temperature in Fahrenheit
        liquid_present: Liquid level sensor reading (0 or 1)
        ph_value: pH reading (optional, defaults to reading from sensor)

    Returns:
        dict: Formatted sensor data
        str: System status
    """
    try:
        # Get pH reading if not provided
        if ph_value is None:
            ph_value = ph_sensor.read_ph_sensor()
            if ph_value is None:
                ph_value = 7.0  # Default neutral pH

        # Format sensor data
        sensor_data = {
            "Air Temperature": (
                f"{temp_f:.1f} °F" if temp_f is not None else "No data"
            ),
            "Humidity": (
                f"{humidity:.1f}%" if humidity is not None else "No data"
            ),
            "Pressure": (
                f"{pressure_inhg:.2f} inHg"
                if pressure_inhg is not None
                else "No data"
            ),
            "Water Temperature": (
                f"{water_temp_f:.1f} °F"
                if water_temp_f is not None
                else "No data"
            ),
            "Water Level": (
                "Normal"
                if liquid_present == 1
                else "Low" if liquid_present == 0 else "Unknown"
            ),
            "pH": f"{ph_value:.2f}" if ph_value is not None else "No data",
        }

        # Determine system status
        system_status = "Normal"
        if liquid_present == 0:
            system_status = "Critical"
        elif temp_f is None or humidity is None or water_temp_f is None:
            system_status = "Warning"
        elif water_temp_f is not None and (
            water_temp_f < 65 or water_temp_f > 85
        ):
            system_status = "Warning"

        return sensor_data, system_status

    except Exception as e:
        logger.error(f"Error formatting sensor data for email: {e}")
        return {
            "Air Temperature": "Error",
            "Humidity": "Error",
            "Pressure": "Error",
            "Water Temperature": "Error",
            "Water Level": "Error",
            "pH": "Error",
        }, "Critical"


#
def check_water_level_change(
    current_liquid_present, temp_f, humidity, pressure_inhg, water_temp_f
):
    """
    Check for water level changes and send email alerts.

    Args:
        current_liquid_present (int): Current water level reading (0 or 1)
        temp_f: Current air temperature
        humidity: Current humidity
        pressure_inhg: Current pressure
        water_temp_f: Current water temperature
    """
    global previous_water_level

    if not ENABLE_SCHEDULED_EMAILS:
        return

    try:
        # Initialize previous water level if not set
        if previous_water_level is None:
            previous_water_level = current_liquid_present
            logger.info(
                f"Initial water level: {'Normal' if current_liquid_present == 1 else 'Low'}"
            )
            return

        # Check for water level change
        if current_liquid_present != previous_water_level:
            # Get current pH reading for email
            current_ph = ph_sensor.read_ph_sensor()

            sensor_data, system_status = get_current_sensor_data_for_email(
                temp_f,
                humidity,
                pressure_inhg,
                water_temp_f,
                current_liquid_present,
                current_ph,
            )

            if current_liquid_present == 0:  # Water level dropped to low
                logger.warning("🚨 WATER LEVEL CRITICAL: Sending alert email")
                success = email_notifier.send_alert(
                    recipient_email=None,  # Uses DEFAULT_RECIPIENT_EMAILS for multiple recipients
                    alert_type="CRITICAL - Water Level Low",
                    alert_message="The water level sensor has detected critically low water levels. Immediate attention required!",
                    sensor_data=sensor_data,
                )
                if success:
                    logger.info("✅ Water level critical alert email sent")
                else:
                    logger.error(
                        "❌ Failed to send water level critical alert email"
                    )

            elif current_liquid_present == 1:  # Water level returned to normal
                logger.info("✅ WATER LEVEL RESTORED: Sending recovery email")
                success = email_notifier.send_alert(
                    recipient_email=None,  # Uses DEFAULT_RECIPIENT_EMAILS for multiple recipients
                    alert_type="RECOVERY - Water Level Normal",
                    alert_message="The water level has been restored to normal levels. System recovery confirmed.",
                    sensor_data=sensor_data,
                )
                if success:
                    logger.info("✅ Water level recovery email sent")
                else:
                    logger.error("❌ Failed to send water level recovery email")

            # Update previous water level
            previous_water_level = current_liquid_present

    except Exception as e:
        logger.error(f"Error in check_water_level_change: {e}")


def should_send_daily_email():
    """Check if it's time to send the daily summary email."""
    global last_daily_email_date

    if not ENABLE_SCHEDULED_EMAILS:
        return False

    current_date = datetime.now().date()
    current_time = datetime.now().time()

    # Parse daily email time
    daily_hour, daily_minute = map(int, DAILY_EMAIL_TIME.split(":"))
    daily_time = current_time.replace(
        hour=daily_hour, minute=daily_minute, second=0, microsecond=0
    )

    # Check if we haven't sent today's email and it's past the scheduled time
    if last_daily_email_date != current_date and current_time >= daily_time:
        return True

    return False


def send_daily_summary_email(
    temp_f, humidity, pressure_inhg, water_temp_f, liquid_present
):
    """Send daily summary email."""
    global last_daily_email_date

    try:
        logger.info("📧 Sending daily summary email")
        # Get current pH reading for email
        current_ph = ph_sensor.read_ph_sensor()

        sensor_data, system_status = get_current_sensor_data_for_email(
            temp_f,
            humidity,
            pressure_inhg,
            water_temp_f,
            liquid_present,
            current_ph,
        )

        success = email_notifier.send_status_report(
            recipient_email=None,  # Uses DEFAULT_RECIPIENT_EMAILS for multiple recipients
            sensor_data=sensor_data,
            system_status=system_status,
        )

        if success:
            last_daily_email_date = datetime.now().date()
            logger.info("✅ Daily summary email sent successfully")
        else:
            logger.error("❌ Failed to send daily summary email")

    except Exception as e:
        logger.error(f"Error sending daily summary email: {e}")


def main():
    # Initialize lists to store readings for averaging
    temp_readings = []
    humidity_readings = []
    pressure_readings = []
    water_temp_readings = []
    ph_readings = []

    # Send initial reading on startup
    initial_reading_sent = False

    try:
        while True:
            # Check for scheduled emails before sensor readings
            if ENABLE_SCHEDULED_EMAILS:
                # Get current sensor readings for email scheduling
                current_temp_f, current_humidity, current_pressure_inhg = (
                    sensor.read_sensors()
                )
                current_water_temp_f = (
                    water_temp_sensor.read_temperature_fahrenheit()
                )
                current_liquid_present = liquid_level_sensor.read_sensor()

                # Check for daily summary email
                if should_send_daily_email():
                    send_daily_summary_email(
                        current_temp_f,
                        current_humidity,
                        current_pressure_inhg,
                        current_water_temp_f,
                        (
                            current_liquid_present
                            if current_liquid_present is not None
                            else 0
                        ),
                    )

            # Read BME680 sensor data using the abstracted module
            temp_f, humidity, pressure_inhg = sensor.read_sensors()

            # Check if BME680 sensor data was retrieved successfully
            if (
                temp_f is not None
                and humidity is not None
                and pressure_inhg is not None
            ):

                # ----------------- READ WATER TEMPERATURE ----------------- #
                # Read water temperature using the abstracted module
                water_temp_f = water_temp_sensor.read_temperature_fahrenheit()

                # ----------------------- READ pH SENSOR ------------------- #
                # Read pH sensor using the abstracted module
                current_ph = ph_sensor.read_ph_sensor()
                if current_ph is not None:
                    ph_readings.append(current_ph)

                # -------------------- STORE READINGS  --------------------- #
                # Store readings for averaging (only store valid readings)
                temp_readings.append(temp_f)
                humidity_readings.append(humidity)
                pressure_readings.append(pressure_inhg)
                if water_temp_f is not None:
                    water_temp_readings.append(water_temp_f)

                logger.info(
                    f"Reading {len(temp_readings)}/20: {temp_f:.1f} °F | {humidity:.1f}% | {pressure_inhg:.2f} inHg"
                )
                if water_temp_f is not None:
                    logger.info(f"Water Temperature: {water_temp_f:.1f} °F")
                else:
                    logger.warning("Failed to read water temperature")

                if current_ph is not None:
                    logger.info(f"pH: {current_ph:.2f}")
                else:
                    logger.warning("Failed to read pH sensor")

                # Send initial reading on startup
                if not initial_reading_sent:
                    # ------------------- READ pH SENSOR ------------------- #
                    # Read pH sensor using the abstracted module
                    ph = ph_sensor.read_ph_sensor()
                    if ph is None:
                        ph = 7.0  # Default to neutral pH if sensor fails
                        logger.warning(
                            "Failed to read pH sensor, using default value 7.0"
                        )

                    # ------------ READ LIQUID LEVEL SENSOR ---------------- #
                    # Read liquid level sensor before sending to ThingSpeak
                    liquid_present = liquid_level_sensor.read_sensor()
                    if liquid_present is None:
                        liquid_present = 0  # Default to no liquid if error

                    # Check for water level changes (email alerts)
                    if ENABLE_SCHEDULED_EMAILS:
                        check_water_level_change(
                            liquid_present,
                            temp_f,
                            humidity,
                            pressure_inhg,
                            water_temp_f,
                        )

                    # Send initial reading
                    logger.info("Sending initial reading to ThingSpeak")
                    thingspeak_send(
                        temp_f,
                        humidity,
                        pressure_inhg,
                        water_temp_f if water_temp_f is not None else 0,
                        liquid_present,
                        ph,
                    )
                    initial_reading_sent = True

                # Check if we have enough readings for averaging
                if len(temp_readings) >= READINGS_PER_CYCLE:
                    # Calculate averages using trimmed mean (remove outliers)
                    avg_temp = calculate_trimmed_mean(temp_readings)
                    avg_humidity = calculate_trimmed_mean(humidity_readings)
                    avg_pressure = calculate_trimmed_mean(pressure_readings)

                    # Average water temperature (only if we have readings)
                    if water_temp_readings:
                        avg_water_temp = calculate_trimmed_mean(
                            water_temp_readings
                        )
                    else:
                        # If no water temp readings in this cycle, try to get a current reading
                        current_water_temp = (
                            water_temp_sensor.read_temperature_fahrenheit()
                        )
                        if current_water_temp is not None:
                            avg_water_temp = current_water_temp
                        else:
                            avg_water_temp = 0
                            logger.warning(
                                "No water temperature readings available for averaging"
                            )

                    # Average pH (only if we have readings)
                    if ph_readings:
                        avg_ph = calculate_trimmed_mean(ph_readings)
                    else:
                        # If no pH readings in this cycle, try to get a current reading
                        current_ph = ph_sensor.read_ph_sensor()
                        if current_ph is not None:
                            avg_ph = current_ph
                        else:
                            avg_ph = 7.0  # Default to neutral pH
                            logger.warning(
                                "No pH readings available for averaging, using default 7.0"
                            )

                    # -------------- READ LIQUID LEVEL SENSOR -------------- #
                    # Read liquid level sensor before sending to ThingSpeak
                    liquid_present = liquid_level_sensor.read_sensor()
                    if liquid_present is None:
                        liquid_present = 0  # Default to no liquid if error

                    # Check for water level changes (email alerts)
                    if ENABLE_SCHEDULED_EMAILS:
                        check_water_level_change(
                            liquid_present,
                            avg_temp,
                            avg_humidity,
                            avg_pressure,
                            avg_water_temp,
                        )

                    # Log averaged values
                    logger.info(
                        f"=== AVERAGED READINGS ({len(temp_readings)} samples) ==="
                    )
                    logger.info(f"Avg Temperature: {avg_temp:.1f} °F")
                    logger.info(f"Avg Humidity: {avg_humidity:.1f}%")
                    logger.info(f"Avg Pressure: {avg_pressure:.2f} inHg")
                    if water_temp_readings:
                        logger.info(
                            f"Avg Water Temperature: {avg_water_temp:.1f} °F ({len(water_temp_readings)} samples)"
                        )
                    if ph_readings:
                        logger.info(
                            f"Avg pH: {avg_ph:.2f} ({len(ph_readings)} samples)"
                        )

                    # Send averaged data to ThingSpeak
                    thingspeak_send(
                        avg_temp,
                        avg_humidity,
                        avg_pressure,
                        avg_water_temp,
                        liquid_present,
                        avg_ph,
                    )

                    # Clear the reading lists for the next cycle
                    temp_readings.clear()
                    humidity_readings.clear()
                    pressure_readings.clear()
                    water_temp_readings.clear()
                    ph_readings.clear()

                # Sleep for 30 seconds before next reading
                sleep(SENSOR_READ_INTERVAL)
            else:
                logger.warning("Failed to get BME680 sensor data")
                sleep(5)  # Short sleep before retrying

    except KeyboardInterrupt:
        logger.info("Bye!")
        # Clean up sensor resources if needed
        try:
            if "liquid_level_sensor" in globals():
                liquid_level_sensor.close()
        except Exception:
            pass
        exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Clean up sensor resources if needed
        try:
            if "liquid_level_sensor" in globals():
                liquid_level_sensor.close()
        except Exception:
            pass
        # Sleep before potential restart
        sleep(600)


# ---------------------------- THINGSPEAK SEND ----------------------------- #
def thingspeak_send(temp, hum, bp, water_temp, liquid_level, ph):
    """Update the ThingSpeak channel using the requests library"""
    logger.info("Update Thingspeak Channel")

    # Each field number corresponds to a field in ThingSpeak
    params = {
        "api_key": TS_KEY,
        "field1": temp,
        "field2": hum,
        "field3": bp,
        "field4": water_temp,
        "field5": liquid_level,
        "field6": ph,
    }

    try:
        # Update data on Thingspeak
        ts_update = requests.get(
            "https://api.thingspeak.com/update", params=params, timeout=30
        )

        # Was the update successful?
        if ts_update.status_code == requests.codes.ok:
            logger.info("Data Received!")
        else:
            logger.error("Error Code: " + str(ts_update.status_code))

        # Print ThingSpeak response to console
        # ts_update.text is the thingspeak data entry number in the channel
        logger.info(f"ThingSpeak Channel Entry: {ts_update.text}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error sending to ThingSpeak: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in thingspeak_send: {e}")


# If a standalone program, call the main function
# Else, use as a module
if __name__ == "__main__":
    logger.info("Starting sensors ThingSpeak service...")
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        # Clean up sensor resources
        try:
            if "liquid_level_sensor" in globals():
                liquid_level_sensor.close()
        except Exception:
            pass
        exit(0)
    except Exception as e:
        logger.critical(f"Critical error in main: {e}")
        # Clean up sensor resources
        try:
            if "liquid_level_sensor" in globals():
                liquid_level_sensor.close()
        except Exception:
            pass
        exit(1)
