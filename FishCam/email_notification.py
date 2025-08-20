#!/usr/bin/env python3
"""
Filename: email_notification.py
Description: Email notification system using Gmail SMTP
Provides email sending capabilities for aquaponics monitoring system
Can be used as a standalone program or imported as a module
"""

import smtplib
import logging
import sys
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# Import configuration
from aquaponics_config import (
    SMTP_SERVER, SMTP_PORT, EMAIL_TIMEOUT,
    DEFAULT_SENDER_EMAIL, DEFAULT_SENDER_PASSWORD,
    DEFAULT_RECIPIENT_EMAILS, SUBJECT_PREFIX, DEFAULT_SUBJECT,
    HTML_TEMPLATE_DIR, ALERT_EMAIL_TEMPLATE, STATUS_REPORT_TEMPLATE
)

# --------------------------- LOGGING SETUP -------------------------------- #
# Configure logging for this module when imported or run standalone
# This ensures email events are always logged to the appropriate log file

def _setup_email_logging():
    """Setup logging configuration for email notifications."""
    logger = logging.getLogger(__name__)
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger
    
    # Create logs directory relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure log formatter
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    
    # File handler with daily rotation, keep 7 days
    log_file_path = os.path.join(logs_dir, "email_notification.log")
    file_handler = TimedRotatingFileHandler(
        log_file_path,
        when="midnight",
        interval=1,
        backupCount=7,
    )
    file_handler.setFormatter(log_formatter)
    # Add date to rotated log files with .log extension  
    file_handler.suffix = ".%Y-%m-%d.log"
    file_handler.extMatch = re.compile(r"^\.\d{4}-\d{2}-\d{2}\.log$")
    
    # Console handler (only when run standalone)
    if __name__ == "__main__":
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)
    
    # Add file handler
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent duplicate messages
    
    return logger

# Setup logging when module is imported
logger = _setup_email_logging()


class EmailNotifier:
    """
    Email notification system for sending alerts and status updates.
    Uses Gmail SMTP with TLS encryption for secure email delivery.
    """

    def __init__(
        self,
        sender_email=None,
        sender_password=None,
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
    ):
        """
        Initialize the email notifier with sender credentials.

        Args:
            sender_email (str): Gmail address to send from
            sender_password (str): Gmail App Password (not regular password)
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP server port
        """
        self.sender_email = sender_email or DEFAULT_SENDER_EMAIL
        self.sender_password = sender_password or DEFAULT_SENDER_PASSWORD
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

        # Validate email configuration
        if "@" not in self.sender_email or "gmail.com" not in self.sender_email:
            logger.warning("Sender email may not be a valid Gmail address")

        logger.info(f"Email notifier initialized for {self.sender_email}")

    def _load_html_template(self, template_name):
        """
        Load HTML template from file.
        
        Args:
            template_name (str): Name of the template file
            
        Returns:
            str: HTML template content, or None if file not found
        """
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(script_dir, HTML_TEMPLATE_DIR, template_name)
            
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"HTML template not found: {template_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading HTML template {template_name}: {e}")
            return None

    def _generate_message_id(self):
        """
        Generate a unique Message-ID header for better email deliverability.
        
        Returns:
            str: Unique message ID
        """
        import uuid
        import socket
        
        # Get hostname or use a default
        try:
            hostname = socket.getfqdn()
            if not hostname or hostname == 'localhost':
                hostname = "wncc-aquaponics.local"
        except:
            hostname = "wncc-aquaponics.local"
            
        # Generate unique ID
        unique_id = str(uuid.uuid4())
        timestamp = str(int(datetime.now().timestamp()))
        
        return f"<{timestamp}.{unique_id}@{hostname}>"

    def _normalize_recipients(self, recipients):
        """
        Normalize recipients to a list format.
        
        Args:
            recipients (str or list): Email address(es) to send to
            
        Returns:
            list: List of email addresses
        """
        if isinstance(recipients, str):
            return [recipients]
        elif isinstance(recipients, list):
            return recipients
        else:
            logger.warning(f"Invalid recipient type: {type(recipients)}, using default")
            return DEFAULT_RECIPIENT_EMAILS

    def send_email(
        self,
        recipient_email=None,
        subject="Test Subject",
        html_message=None,
        attachments=None,
    ):
        """
        Send an HTML email using Gmail SMTP to one or more recipients.

        Args:
            recipient_email (str or list): Email address(es) to send to. 
                                         Can be a single email string or list of emails.
                                         If None, uses DEFAULT_RECIPIENT_EMAILS
            subject (str): Email subject line
            html_message (str): HTML message body (required)
            attachments (list, optional): List of file paths to attach

        Returns:
            bool: True if email sent successfully to all recipients, False otherwise
        """
        try:
            # Validate HTML message is provided
            if not html_message:
                logger.error("HTML message is required")
                return False
                
            # Handle recipients
            if recipient_email is None:
                recipients = DEFAULT_RECIPIENT_EMAILS
            else:
                recipients = self._normalize_recipients(recipient_email)
            
            # Validate we have at least one recipient
            if not recipients:
                logger.error("No recipients specified")
                return False

            # Create message container for HTML only
            msg = MIMEMultipart("alternative")
            msg["From"] = f"WNCC Aquaponics System <{self.sender_email}>"  # Add friendly name
            msg["To"] = ", ".join(recipients)  # Join multiple recipients with commas
            msg["Subject"] = subject
            
            # Add anti-spam headers to improve deliverability
            msg["Reply-To"] = self.sender_email
            msg["Return-Path"] = self.sender_email
            msg["X-Mailer"] = "WNCC Aquaponics Monitoring System v1.0"
            msg["X-Priority"] = "3"  # Normal priority (1=High, 3=Normal, 5=Low)
            msg["Message-ID"] = self._generate_message_id()
            msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

            # Add HTML part only
            html_part = MIMEText(html_message, "html")
            msg.attach(html_part)

            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        self._add_attachment(msg, file_path)
                    else:
                        logger.warning(
                            f"Attachment file not found: {file_path}"
                        )

            # Send the email to all recipients
            return self._send_message(msg, recipients)

        except Exception as e:
            logger.error(f"Error creating email message: {e}")
            return False

    def send_alert(
        self, recipient_email=None, alert_type="Alert", alert_message="", sensor_data=None
    ):
        """
        Send a formatted alert email for aquaponics system issues.

        Args:
            recipient_email (str or list): Email address(es) to send alert to.
                                         If None, uses DEFAULT_RECIPIENT_EMAILS
            alert_type (str): Type of alert (e.g., "Temperature", "pH", "Water Level")
            alert_message (str): Detailed alert message
            sensor_data (dict, optional): Current sensor readings

        Returns:
            bool: True if alert sent successfully, False otherwise
        """
        try:
            # Create alert subject
            subject = f"{SUBJECT_PREFIX} {alert_type} Alert"

            # Create formatted timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create HTML version using template
            html_template = self._load_html_template(ALERT_EMAIL_TEMPLATE)
            html_message = None
            
            if html_template:
                # Generate sensor data table if sensor data is provided
                sensor_data_table = ""
                if sensor_data:
                    sensor_data_table = """
        <div style="margin: 20px 0;">
            <h3 style="color: #495057; margin: 0 0 15px 0;">Current System Readings:</h3>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid #dee2e6;">
                <thead>
                    <tr style="background-color: #e9ecef;">
                        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Sensor</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Reading</th>
                    </tr>
                </thead>
                <tbody>
"""
                    for sensor, value in sensor_data.items():
                        sensor_data_table += f"""
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{sensor}</td>
                        <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-weight: bold;">{value}</td>
                    </tr>
"""
                    sensor_data_table += """
                </tbody>
            </table>
        </div>
"""
                
                # Replace placeholders in template
                html_message = html_template.format(
                    alert_type=alert_type,
                    timestamp=timestamp,
                    alert_message=alert_message,
                    sensor_data_table=sensor_data_table
                )
            else:
                # Fallback to inline HTML if template not available
                html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WNCC Aquaponics System Alert</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    
    <div style="background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
        <h1 style="margin: 0; font-size: 24px;">🔔 WNCC Aquaponics System Alert</h1>
        <p style="margin: 10px 0 0 0; font-size: 14px;">Western Nebraska Community College</p>
    </div>
    
    <div style="background-color: #fff; border: 1px solid #ddd; padding: 20px; border-radius: 0 0 8px 8px;">
        <p style="font-size: 16px; margin-top: 0;">Dear WNCC Aquaponics Team,</p>
        
        <p>This is an automated notification from the WNCC Aquaponics Monitoring System regarding a system condition that requires attention.</p>
        
        <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
            <h2 style="color: #856404; margin: 0 0 10px 0; font-size: 18px;">System Alert Details</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px; font-weight: bold; background-color: #fdf6e3;">Alert Type:</td>
                    <td style="padding: 8px; background-color: #fdf6e3;">{alert_type}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Date/Time:</td>
                    <td style="padding: 8px;">{timestamp}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; background-color: #fdf6e3;">Location:</td>
                    <td style="padding: 8px; background-color: #fdf6e3;">WNCC Aquaponics Laboratory</td>
                </tr>
            </table>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #495057; margin: 0 0 10px 0;">Alert Description:</h3>
            <p style="margin: 0; font-size: 14px;">{alert_message}</p>
        </div>
"""

                if sensor_data:
                    html_message += """
        <div style="margin: 20px 0;">
            <h3 style="color: #495057; margin: 0 0 15px 0;">Current System Readings:</h3>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid #dee2e6;">
                <thead>
                    <tr style="background-color: #e9ecef;">
                        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Sensor</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Reading</th>
                    </tr>
                </thead>
                <tbody>
"""
                    for sensor, value in sensor_data.items():
                        html_message += f"""
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{sensor}</td>
                        <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-weight: bold;">{value}</td>
                    </tr>
"""
                    html_message += """
                </tbody>
            </table>
        </div>
"""

                html_message += """
        <div style="background-color: #d1ecf1; border-left: 4px solid #bee5eb; padding: 15px; margin: 20px 0;">
            <h3 style="color: #0c5460; margin: 0 0 10px 0;">Recommended Action:</h3>
            <p style="margin: 0; color: #0c5460;">Please review the aquaponics system at your earliest convenience to ensure optimal operation.</p>
        </div>
        
        <hr style="border: none; border-top: 1px solid #dee2e6; margin: 20px 0;">
        
        <div style="font-size: 12px; color: #6c757d;">
            <p><strong>System Information:</strong></p>
            <ul style="margin: 5px 0; padding-left: 20px;">
                <li>Monitoring System: WNCC Aquaponics v1.0</li>
                <li>Installation: Western Nebraska Community College</li>
                <li>Department: Information Technology Program</li>
            </ul>
            
            <p style="margin-top: 15px;">
                This alert was generated automatically by the WNCC Aquaponics Monitoring System.<br>
                For technical support, please contact the Information Technology Program.
            </p>
            
            <p style="margin-top: 10px; font-style: italic;">
                Best regards,<br>
                WNCC Aquaponics Monitoring System
            </p>
        </div>
    </div>
</body>
</html>
"""

            return self.send_email(
                recipient_email, subject, html_message
            )

        except Exception as e:
            logger.error(f"Error sending alert email: {e}")
            return False

    def send_status_report(
        self,
        recipient_email=None,
        sensor_data=None,
        system_status="Normal",
    ):
        """
        Send a system status report email.

        Args:
            recipient_email (str or list): Email address(es) to send report to.
                                         If None, uses DEFAULT_RECIPIENT_EMAILS
            sensor_data (dict): Current sensor readings
            system_status (str): Overall system status

        Returns:
            bool: True if report sent successfully, False otherwise
        """
        try:
            # Default sensor data if none provided
            if sensor_data is None:
                sensor_data = {
                    "Temperature": "No data",
                    "Humidity": "No data",
                    "pH": "No data",
                    "Water Temperature": "No data",
                }

            subject = f"{SUBJECT_PREFIX} Daily Status Report"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Load HTML template and build content
            html_template = self._load_html_template("status_report.html")
            if html_template:
                # Generate sensor data table rows
                sensor_rows = ""
                for sensor, value in sensor_data.items():
                    sensor_rows += f"""
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{sensor}</td>
                        <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-weight: bold; color: #28a745;">{value}</td>
                    </tr>"""

                # Set status color
                status_color = "#4caf50" if system_status == "Normal" else "#f44336"

                # Replace placeholders in template
                html_message = html_template.format(
                    timestamp=timestamp,
                    system_status=system_status,
                    status_color=status_color,
                    sensor_data_rows=sensor_rows
                )
            else:
                # Fallback HTML if template loading fails
                status_color = "#4caf50" if system_status == "Normal" else "#f44336"
                html_message = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>WNCC Aquaponics Status Report</h2>
    <p><strong>Report Generated:</strong> {timestamp}</p>
    <p><strong>System Status:</strong> <span style="color: {status_color};">{system_status}</span></p>
    <h3>Current Readings:</h3>
    <ul>
"""
                for sensor, value in sensor_data.items():
                    html_message += f"        <li>{sensor}: {value}</li>\n"
                html_message += """
    </ul>
    <p>All monitored systems are operating within normal parameters.</p>
</body>
</html>
"""

            return self.send_email(
                recipient_email, subject, html_message
            )

        except Exception as e:
            logger.error(f"Error sending status report: {e}")
            return False

    def _add_attachment(self, msg, file_path):
        """
        Add a file attachment to the email message.

        Args:
            msg (MIMEMultipart): Email message object
            file_path (str): Path to file to attach
        """
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            filename = os.path.basename(file_path)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg.attach(part)
            logger.debug(f"Added attachment: {filename}")

        except Exception as e:
            logger.error(f"Error adding attachment {file_path}: {e}")

    def _send_message(self, msg, recipients):
        """
        Send the email message using SMTP to one or more recipients.

        Args:
            msg (MIMEMultipart): Email message to send
            recipients (str or list): Recipient email address(es)

        Returns:
            bool: True if sent successfully to all recipients, False otherwise
        """
        try:
            # Normalize recipients to list
            recipient_list = self._normalize_recipients(recipients)
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)

            # Enable TLS encryption
            server.starttls()

            # Login with sender credentials
            server.login(self.sender_email, self.sender_password)

            # Send email to all recipients
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient_list, text)
            server.quit()

            # Log successful delivery
            if len(recipient_list) == 1:
                logger.info(f"Email sent successfully to {recipient_list[0]}")
            else:
                logger.info(f"Email sent successfully to {len(recipient_list)} recipients: {', '.join(recipient_list)}")
            
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error(
                "SMTP Authentication failed. Check email and password."
            )
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def test_connection(self):
        """
        Test the email connection and authentication.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.quit()

            logger.info("Email connection test successful")
            return True

        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False


# Convenience functions for backwards compatibility
def send_alert_email(
    recipient_email=None, alert_type="Alert", alert_message="", sensor_data=None
):
    """
    Convenience function to send an alert email.

    Args:
        recipient_email (str or list): Email address(es) to send alert to.
                                     If None, uses DEFAULT_RECIPIENT_EMAILS
        alert_type (str): Type of alert
        alert_message (str): Alert message
        sensor_data (dict, optional): Current sensor readings

    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        notifier = EmailNotifier()
        return notifier.send_alert(
            recipient_email, alert_type, alert_message, sensor_data
        )
    except Exception as e:
        logger.error(f"Failed to send alert email: {e}")
        return False


def send_status_email(
    recipient_email=None,
    sensor_data=None,
    system_status="Normal",
):
    """
    Convenience function to send a status report email.

    Args:
        recipient_email (str or list): Email address(es) to send report to.
                                     If None, uses DEFAULT_RECIPIENT_EMAILS
        sensor_data (dict): Current sensor readings
        system_status (str): System status

    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        notifier = EmailNotifier()
        return notifier.send_status_report(
            recipient_email, sensor_data, system_status
        )
    except Exception as e:
        logger.error(f"Failed to send status email: {e}")
        return False


# Test function for standalone execution
def main():
    """Test function to verify email functionality."""
    print("Testing Email Notification System...")
    print("=" * 50)

    try:
        # Create email notifier
        notifier = EmailNotifier()

        # Test connection
        print("\n1. Testing email connection...")
        if notifier.test_connection():
            print("✅ Connection test successful!")
        else:
            print("❌ Connection test failed!")
            return

        # Test simple email
        print("\n2. Sending test email...")
        test_subject = "Email System Test"
        test_html_message = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Email System Test</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
        <h1 style="margin: 0;">🔧 Email System Test</h1>
        <p style="margin: 10px 0 0 0;">WNCC Aquaponics Monitoring System</p>
    </div>
    <div style="background-color: #fff; border: 1px solid #ddd; padding: 20px; border-radius: 0 0 8px 8px;">
        <p>This is a test email from the aquaponics monitoring system.</p>
        <p>If you received this email, the HTML email system is working correctly!</p>
    </div>
</body>
</html>
"""

        if notifier.send_email(subject=test_subject, html_message=test_html_message):
            print("✅ Test email sent successfully!")
        else:
            print("❌ Failed to send test email!")

        # Test alert email
        print("\n3. Sending test alert...")
        test_sensor_data = {
            "Temperature": "75.2°F",
            "Humidity": "65.8%",
            "pH": "6.8",
            "Water Temperature": "72.1°F",
        }

        if notifier.send_alert(
            None,  # Use DEFAULT_RECIPIENT_EMAILS
            "Temperature",
            "Water temperature is above normal range",
            test_sensor_data,
        ):
            print("✅ Test alert sent successfully!")
        else:
            print("❌ Failed to send test alert!")

        # Test status report
        print("\n4. Sending test status report...")
        if notifier.send_status_report(
            None, test_sensor_data  # Use DEFAULT_RECIPIENT_EMAILS
        ):
            print("✅ Test status report sent successfully!")
        else:
            print("❌ Failed to send test status report!")

        print("\n" + "=" * 50)
        print("Email testing completed!")

    except KeyboardInterrupt:
        print("\nTesting interrupted by user")
    except Exception as e:
        print(f"Error during testing: {e}")


if __name__ == "__main__":
    # When run directly as a script, the logging is already configured by _setup_email_logging()
    # Just run the main test function
    main()
