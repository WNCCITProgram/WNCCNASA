"""
Configuration file for the Aquaponics Monitoring System
Centralizes all configurable parameters for easy maintenance
"""

# Sensor Reading Configuration
SENSOR_READ_INTERVAL = 15  # seconds between sensor readings
THINGSPEAK_INTERVAL = 600  # seconds between ThingSpeak updates (10 minutes)

# Calculated values based on intervals
READINGS_PER_CYCLE = THINGSPEAK_INTERVAL // SENSOR_READ_INTERVAL

# Email Configuration
ENABLE_SCHEDULED_EMAILS = True
DAILY_EMAIL_TIME = "06:00"  # HH:MM format for daily status email

# Email SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # TLS port for Gmail
EMAIL_TIMEOUT = 30  # Connection timeout in seconds

# Default email settings (can be overridden)
DEFAULT_SENDER_EMAIL = "wnccrobotics@gmail.com"
# Use App Password, not regular password
DEFAULT_SENDER_PASSWORD = "loyqlzkxisojeqsr"

# Multiple recipients - add more email addresses here
DEFAULT_RECIPIENT_EMAILS = [
    "williamaloring@gmail.com",
    "williamloring@hotmail.com",
    "sarah.trook31@gmail.com",
    # "admin@wncc.edu",
    # "tech@wncc.edu",
]

# Email template constants
SUBJECT_PREFIX = "Aquaponics "
DEFAULT_SUBJECT = f"{SUBJECT_PREFIX} System Notification"

# Data Processing Configuration
TRIM_PERCENT = (
    0.05  # Percentage to trim from each end for outlier removal (10%)
)

# Sensor Thresholds for Alerts
WATER_TEMP_MIN = 65.0  # Fahrenheit
WATER_TEMP_MAX = 85.0  # Fahrenheit

# System Configuration
LOG_BACKUP_COUNT = 7  # Number of log files to keep
LOG_ROTATION = "midnight"  # When to rotate logs

# Network Configuration
THINGSPEAK_TIMEOUT = 30  # seconds
RETRY_DELAY = 5  # seconds to wait before retrying failed operations
RESTART_DELAY = (
    600  # seconds to wait before system restart after critical error
)

# Default pH Value (when sensor not available)
DEFAULT_PH = 7.0

# HTML Template File Paths
HTML_TEMPLATE_DIR = "html_templates"
ALERT_EMAIL_TEMPLATE = "alert_email.html"
STATUS_REPORT_TEMPLATE = "status_report.html"
