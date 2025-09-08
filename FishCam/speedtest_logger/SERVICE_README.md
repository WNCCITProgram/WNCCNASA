# Speedtest Logger Service Wrapper

This directory contains an optimized service wrapper for running the speedtest logger as a systemd service on Raspberry Pi.

## Files

- `speedtest_logger.py` - Main speedtest logging application (optimized for service mode)
- `speedtest_service.py` - Service wrapper with proper signal handling and error management
- `speedtest-service.service` - Systemd service configuration file
- `install_service_wrapper.sh` - Installation script for the service wrapper
- `test_service.py` - Test script to verify the service wrapper works correctly

## Features

### Service Wrapper Features (`speedtest_service.py`)
- **Graceful shutdown handling** - Responds properly to SIGTERM/SIGINT signals
- **Error recovery** - Continues running even if individual tests fail
- **Service-friendly logging** - Uses systemd journal for logging
- **Environment validation** - Checks for required dependencies before starting
- **Signal handling** - Supports reload (SIGHUP) on Unix systems
- **Resource management** - Proper cleanup on shutdown

### Logger Optimizations (`speedtest_logger.py`)
- **Service mode support** - Disables rich console output when running as service
- **Better error handling** - More robust error handling for network issues
- **Service-friendly output** - Optimized logging for systemd journal

## Installation

### Quick Install (Recommended)
```bash
# Make the installation script executable
chmod +x install_service_wrapper.sh

# Run the installation
./install_service_wrapper.sh
```

### Manual Installation
```bash
# Install dependencies
pip3 install speedtest-cli rich schedule --user

# Create installation directory
sudo mkdir -p /home/pi/speedtest-logger

# Copy files
sudo cp speedtest_logger.py /home/pi/speedtest-logger/
sudo cp speedtest_service.py /home/pi/speedtest-logger/
sudo chmod +x /home/pi/speedtest-logger/*.py

# Install service
sudo cp speedtest-service.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable speedtest-service
sudo systemctl start speedtest-service
```

## Testing

Before installing as a service, test the wrapper:

```bash
# Run the test suite
python3 test_service.py

# Test the service wrapper directly
python3 speedtest_service.py
```

## Service Management

```bash
# Check service status
sudo systemctl status speedtest-service

# Start/stop/restart
sudo systemctl start speedtest-service
sudo systemctl stop speedtest-service
sudo systemctl restart speedtest-service

# View logs
sudo journalctl -u speedtest-service -f

# Disable auto-start
sudo systemctl disable speedtest-service
```

## Configuration

### Environment Variables
- `SPEEDTEST_SERVICE_MODE=true` - Enables service mode (set automatically by systemd)

### Service Configuration
Edit `/etc/systemd/system/speedtest-service.service` to modify:
- Working directory
- User/group
- Resource limits
- Environment variables

After editing, reload the service:
```bash
sudo systemctl daemon-reload
sudo systemctl restart speedtest-service
```

### Logger Configuration
Edit the constants in `speedtest_logger.py`:
- `TEST_INTERVAL_MINUTES` - How often to run tests (default: 60)
- `NUM_RUNS_TO_AVERAGE` - Number of tests to average (default: 3)
- `LOG_FILE_PATH` - Log file location (default: "speedtest_log.txt")

## Log Files

- **Service logs**: `sudo journalctl -u speedtest-service`
- **Speed test data**: `/home/pi/speedtest-logger/speedtest_log.txt`
- **Rotating logs**: Files are rotated daily and kept for 7 days

## Troubleshooting

### Service won't start
```bash
# Check service status and logs
sudo systemctl status speedtest-service
sudo journalctl -u speedtest-service -n 50

# Check file permissions
ls -la /home/pi/speedtest-logger/

# Verify dependencies
python3 test_service.py
```

### Network issues
The service is designed to handle network outages gracefully:
- Individual test failures don't stop the service
- Tests are retried on the next scheduled interval
- Network connectivity is checked before running tests

### Memory issues
The service includes memory limits in the systemd configuration:
- Default limit: 512M
- Modify in `/etc/systemd/system/speedtest-service.service`

## Upgrading

To upgrade the service:
```bash
# Stop the service
sudo systemctl stop speedtest-service

# Update files
sudo cp speedtest_logger.py /home/pi/speedtest-logger/
sudo cp speedtest_service.py /home/pi/speedtest-logger/

# Restart the service
sudo systemctl start speedtest-service
```

## Security Features

The service runs with several security enhancements:
- Non-privileged user (`pi`)
- Private temporary directory
- Read-only system protection
- Limited process count
- Memory limits

## Differences from Original

### Original `speedtest_logger.py`
- Designed for interactive use
- Rich console output
- Manual start/stop only

### Service Wrapper Version
- Optimized for systemd service
- Proper signal handling
- Journal logging
- Automatic restart on failure
- Service mode detection
- Better error recovery

The service wrapper provides a production-ready way to run the speedtest logger continuously with proper system integration.
