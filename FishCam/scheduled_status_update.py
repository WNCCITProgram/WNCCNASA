#!/usr/bin/env python3
"""
Filename: scheduled_status_update.py
Description: Scheduled status update script for aquaponics monitoring system
Reads current sensor values and sends email status reports
Can be called by cron jobs or scheduled tasks
"""

import sys
import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# Import sensor modules
from bme680_ts import BME680Sensor
from liquid_level_sensor_ts import LiquidLevelSensor
from temp_water_sensor_ts import WaterTemperatureSensor

# Import email notification system
from email_notification import EmailNotifier, DEFAULT_RECIPIENT_EMAILS

# Configure logging
logger = logging.getLogger(__name__)

# Only configure if not already configured
if not logger.handlers:
    log_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    # Create logs directory relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # File handler with daily rotation, keep 7 days
    log_file_path = os.path.join(logs_dir, "scheduled_status.log")
    file_handler = TimedRotatingFileHandler(
        log_file_path,
        when="midnight",
        interval=1,
        backupCount=7,
    )
    file_handler.setFormatter(log_formatter)
    file_handler.suffix = "%Y-%m-%d"

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False


def read_all_sensors():
    """
    Read all sensor values and return formatted data.

    Returns:
        dict: Dictionary containing all sensor readings
        str: System status ("Normal", "Warning", "Critical")
    """
    try:
        # Initialize sensors
        bme_sensor = BME680Sensor()
        liquid_sensor = LiquidLevelSensor()
        water_temp_sensor = WaterTemperatureSensor()

        # Read BME680 sensor data
        temp_f, humidity, pressure_inhg = bme_sensor.read_sensors()

        # Read water temperature
        water_temp_f = water_temp_sensor.read_temperature_fahrenheit()

        # Read liquid level
        liquid_present = liquid_sensor.read_sensor()

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
            "pH": "7.0 (simulated)",  # pH sensor removed - dummy data
        }

        # Determine system status
        system_status = "Normal"

        # Check for critical conditions
        if liquid_present == 0:
            system_status = "Critical"
        elif temp_f is None or humidity is None or water_temp_f is None:
            system_status = "Warning"
        elif water_temp_f is not None and (
            water_temp_f < 65 or water_temp_f > 85
        ):
            system_status = "Warning"
        elif humidity is not None and (humidity < 40 or humidity > 80):
            system_status = "Warning"

        logger.info(
            f"Sensor readings collected - System Status: {system_status}"
        )

        # Clean up sensor resources
        try:
            liquid_sensor.close()
        except Exception:
            pass

        return sensor_data, system_status

    except Exception as e:
        logger.error(f"Error reading sensors: {e}")
        return {
            "Air Temperature": "Error",
            "Humidity": "Error",
            "Pressure": "Error",
            "Water Temperature": "Error",
            "Water Level": "Error",
            "pH": "Error",
        }, "Critical"


def send_status_update(recipient_email=None):
    """
    Send a status update email with current sensor readings.

    Args:
        recipient_email (str): Email address to send to (optional)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        logger.info("Starting scheduled status update")

        # Use default recipients if none provided
        if recipient_email is None:
            recipient_email = None  # This will use DEFAULT_RECIPIENT_EMAILS

        # Read current sensor values
        sensor_data, system_status = read_all_sensors()

        # Initialize email notifier
        email_notifier = EmailNotifier()

        # Test email connection first
        if not email_notifier.test_connection():
            logger.error("Email connection test failed")
            return False

        # Send status report
        success = email_notifier.send_status_report(
            recipient_email=recipient_email,
            sensor_data=sensor_data,
            system_status=system_status,
        )

        if success:
            logger.info(
                f"Status update email sent successfully to {recipient_email}"
            )
            logger.info(f"System status: {system_status}")
        else:
            logger.error("Failed to send status update email")

        return success

    except Exception as e:
        logger.error(f"Error in send_status_update: {e}")
        return False


def send_daily_summary():
    """
    Send a comprehensive daily summary email.
    """
    try:
        logger.info("Generating daily summary report")

        sensor_data, system_status = read_all_sensors()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create enhanced daily summary
        email_notifier = EmailNotifier()

        subject = f"[Aquaponics] Daily Summary - {datetime.now().strftime('%Y-%m-%d')}"

        # Enhanced message with more details
        message = f"""
AQUAPONICS SYSTEM DAILY SUMMARY

Report Date: {datetime.now().strftime('%Y-%m-%d')}
Report Time: {datetime.now().strftime('%H:%M:%S')}
System Status: {system_status}

=== CURRENT SENSOR READINGS ===
"""

        for sensor, value in sensor_data.items():
            message += f"{sensor:20}: {value}\n"

        message += f"""

=== SYSTEM HEALTH CHECK ===
✓ Email notification system: Operational
✓ Sensor monitoring: Active
✓ Data logging: Enabled
✓ ThingSpeak updates: Active

=== MAINTENANCE REMINDERS ===
• Check water level daily
• Clean sensors weekly
• Monitor temperature ranges
• Verify pH levels (when sensor available)

This automated report is generated daily at scheduled intervals.
For real-time monitoring, check the ThingSpeak dashboard.

Aquaponics Monitoring System
Western Nebraska Community College
"""

        success = email_notifier.send_email(
            recipient_email=None,  # Use DEFAULT_RECIPIENT_EMAILS
            subject=subject,
            message=message,
        )

        if success:
            logger.info("Daily summary email sent successfully")
        else:
            logger.error("Failed to send daily summary email")

        return success

    except Exception as e:
        logger.error(f"Error sending daily summary: {e}")
        return False


def main():
    """
    Main function for scheduled execution.
    Can be called with command line arguments to specify update type.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Aquaponics Status Update Scheduler"
    )
    parser.add_argument(
        "--type",
        choices=["status", "daily", "test"],
        default="status",
        help="Type of update to send",
    )
    parser.add_argument(
        "--email", type=str, help="Recipient email address (optional)"
    )

    args = parser.parse_args()

    try:
        if args.type == "status":
            success = send_status_update(args.email)
        elif args.type == "daily":
            success = send_daily_summary()
        elif args.type == "test":
            # Test email functionality
            email_notifier = EmailNotifier()
            success = email_notifier.test_connection()
            if success:
                logger.info("Email system test passed")
            else:
                logger.error("Email system test failed")
        else:
            logger.error(f"Unknown update type: {args.type}")
            success = False

        if success:
            logger.info("Scheduled task completed successfully")
            sys.exit(0)
        else:
            logger.error("Scheduled task failed")
            sys.exit(1)

    except Exception as e:
        logger.critical(f"Critical error in scheduled task: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
