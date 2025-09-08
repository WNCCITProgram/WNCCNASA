#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: speedtest_service.py
Author: William A Loring
Created: 09/03/25
Service wrapper for speedtest_logger.py optimized for systemd service execution
"""
import sys
import os
import signal
import logging
from pathlib import Path
import time

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

try:
    from speedtest_logger import SpeedtestLogger
except ImportError as e:
    print(f"Error importing speedtest_logger: {e}")
    sys.exit(1)


class SpeedtestService:
    """Service wrapper for SpeedtestLogger optimized for systemd."""

    def __init__(self):
        self.speedtest_logger = None
        self.running = False
        self.setup_service_logging()
        
    def interruptible_sleep(self, duration):
        """Sleep for the specified duration but check for interruption every second."""
        for _ in range(int(duration)):
            if not self.running:
                return
            time.sleep(1)
        # Handle fractional seconds
        if duration % 1 > 0 and self.running:
            time.sleep(duration % 1)

    def setup_service_logging(self):
        """Setup logging specifically for service operation."""
        # Configure root logger for service
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        self.logger = logging.getLogger("speedtest_service")
        self.logger.info("Speedtest service wrapper starting...")

    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        signal_names = {signal.SIGTERM: "SIGTERM", signal.SIGINT: "SIGINT"}

        # Add SIGHUP if available (Unix systems)
        sighup_value = getattr(signal, "SIGHUP", None)
        if sighup_value is not None:
            signal_names[sighup_value] = "SIGHUP"

        signal_name = signal_names.get(signum, f"Signal {signum}")
        self.logger.info(
            f"Received {signal_name}, initiating graceful shutdown..."
        )

        # Immediately set running to False for faster response
        self.running = False

        # Handle reload/restart signal (Unix only)
        if sighup_value is not None and signum == sighup_value:
            self.logger.info("Reloading service configuration...")
            self.restart_logger()
        else:
            # Handle termination signals - force shutdown
            self.logger.info("Setting shutdown flag...")
            # For SIGINT (Ctrl+C), ensure we exit quickly
            if signum == signal.SIGINT:
                self.logger.info("SIGINT received - forcing quick shutdown")
                # Give a moment for cleanup, then exit
                import threading
                def delayed_exit():
                    time.sleep(2)
                    if self.running == False:  # Still shutting down
                        self.logger.info("Force exit after timeout")
                        os._exit(0)
                threading.Thread(target=delayed_exit, daemon=True).start()

    def setup_signal_handlers(self):
        """Setup signal handlers for service operation."""
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

        # Only setup SIGHUP on Unix systems
        sighup_value = getattr(signal, "SIGHUP", None)
        if sighup_value is not None:
            signal.signal(sighup_value, self.signal_handler)

    def validate_environment(self):
        """Validate the environment before starting the service."""
        try:
            # Check if we can import required modules
            import speedtest
            import schedule
            # Note: rich is optional and handled by speedtest_logger

            self.logger.info("All required modules are available")
            return True

        except ImportError as e:
            self.logger.error(f"Missing required module: {e}")
            return False

    def restart_logger(self):
        """Restart the speedtest logger (for SIGHUP handling)."""
        if self.speedtest_logger:
            self.logger.info("Stopping current logger instance...")
            # The logger will stop on next iteration due to running=False

        # Wait a moment for cleanup (but be interruptible)
        self.interruptible_sleep(2)

        # Restart
        self.logger.info("Restarting logger...")
        self.start_logger()

    def start_logger(self):
        """Start the speedtest logger."""
        try:
            self.logger.info("Initializing SpeedtestLogger...")

            # Create new logger instance in service mode (no rich formatting)
            self.speedtest_logger = SpeedtestLogger(service_mode=True)

            # Modify the logger to be service-friendly
            self.make_service_friendly()

            self.logger.info("Starting speedtest logging service...")
            self.speedtest_logger.start_logging()

        except Exception as e:
            self.logger.error(f"Failed to start speedtest logger: {e}")
            raise

    def make_service_friendly(self):
        """Modify the speedtest logger for better service operation."""
        if not self.speedtest_logger:
            return

        # Store original scheduled_test method
        original_scheduled_test = self.speedtest_logger.scheduled_test

        def service_scheduled_test():
            """Wrapper for scheduled test that respects service state."""
            if not self.running:
                self.logger.info("Service stopping, skipping scheduled test")
                return

            try:
                original_scheduled_test()
            except Exception as e:
                self.logger.error(f"Error during scheduled test: {e}")
                # Don't exit on single test failure in service mode

        # Replace the method
        self.speedtest_logger.scheduled_test = service_scheduled_test

        # Override the main loop to respect service state
        original_start_logging = self.speedtest_logger.start_logging

        def service_start_logging():
            """Service-friendly version of start_logging."""
            import schedule

            if self.speedtest_logger and hasattr(
                self.speedtest_logger, "logger"
            ):
                self.speedtest_logger.logger.info("Speedtest logger started")

            # Schedule the tests
            from speedtest_logger import TEST_INTERVAL_MINUTES

            if self.speedtest_logger and hasattr(
                self.speedtest_logger, "scheduled_test"
            ):
                schedule.every(TEST_INTERVAL_MINUTES).minutes.do(
                    self.speedtest_logger.scheduled_test
                )

                # Run first test immediately
                self.speedtest_logger.scheduled_test()

            # Service-friendly main loop
            self.logger.info("Entering service main loop...")
            while self.running:
                try:
                    schedule.run_pending()
                    # Use interruptible sleep that checks running flag every second
                    self.interruptible_sleep(60)
                except Exception as e:
                    self.logger.error(f"Error in main loop: {e}")
                    if not self.running:
                        break
                    # Use interruptible sleep after errors too
                    self.interruptible_sleep(60)

            self.logger.info("Service main loop exited")

        # Replace the method
        self.speedtest_logger.start_logging = service_start_logging

    def run(self):
        """Main service run method."""
        try:
            self.logger.info("Starting Speedtest Service...")

            # Validate environment
            if not self.validate_environment():
                self.logger.error("Environment validation failed")
                return 1

            # Setup signal handlers
            self.setup_signal_handlers()

            # Set running flag
            self.running = True

            # Start the logger
            self.start_logger()

            self.logger.info("Speedtest service stopped normally")
            return 0

        except KeyboardInterrupt:
            self.logger.info("Service interrupted by user (KeyboardInterrupt)")
            self.running = False
            return 0
        except Exception as e:
            self.logger.error(f"Service error: {e}")
            self.running = False
            return 1
        finally:
            # Ensure cleanup happens
            self.shutdown()

    def shutdown(self):
        """Graceful shutdown of the service."""
        self.logger.info("Shutting down service...")
        self.running = False

        if self.speedtest_logger:
            # Log shutdown
            if hasattr(self.speedtest_logger, "logger"):
                self.speedtest_logger.logger.info(
                    "Speedtest logger stopped by service"
                )

        self.logger.info("Service shutdown complete")


def main():
    """Service entry point."""
    # Ensure we're in the correct directory
    os.chdir(Path(__file__).parent)

    # Create and run service
    service = SpeedtestService()
    exit_code = service.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
