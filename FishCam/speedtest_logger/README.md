# Speedtest Logger for Raspberry Pi

A systemd service that automatically runs internet speed tests and logs the results.

## Features
- Runs speed tests every 30 minutes
- Averages 3 tests for accuracy
- Logs results to rotating daily files
- Starts automatically on boot
- Beautiful console output with Rich library

## Installation

1. **Download files to your Raspberry Pi:**
   ```bash
   # Clone or download the files to a directory
   wget speedtest_logger.py
   wget speedtest-logger.service
   wget install_service.sh
   wget uninstall_service.sh
   ```

2. **Make scripts executable:**
   ```bash
   chmod +x install_service.sh
   chmod +x uninstall_service.sh
   ```

3. **Run the installation script:**
   ```bash
   ./install_service.sh
   ```

## Usage

### Service Management Commands
```bash
# Check service status
sudo systemctl status speedtest-logger

# Start the service
sudo systemctl start speedtest-logger

# Stop the service
sudo systemctl stop speedtest-logger

# Restart the service
sudo systemctl restart speedtest-logger

# View logs in real-time
sudo journalctl -u speedtest-logger -f

# View recent logs
sudo journalctl -u speedtest-logger -n 50
```

### Log Files
- Log files are stored in `/home/pi/speedtest-logger/`
- Daily rotation with 30-day retention
- Format: `speedtest_log.txt`, `speedtest_log.txt.2025-09-03`, etc.

## Configuration

Edit the constants in `speedtest_logger.py`:
```python
TEST_INTERVAL_MINUTES = 30  # How often to run tests
NUM_RUNS_TO_AVERAGE = 3     # Number of tests to average
LOG_FILE_PATH = "speedtest_log.txt"  # Log file name
```

## Uninstallation

Run the uninstall script:
```bash
./uninstall_service.sh
```

## Troubleshooting

### Service won't start
```bash
# Check detailed logs
sudo journalctl -u speedtest-logger -f

# Check service status
sudo systemctl status speedtest-logger
```

### Missing dependencies
```bash
# Install manually if needed
pip3 install speedtest-cli rich schedule --user
```

### Permission issues
Make sure the service runs as user `pi` and all files are owned by `pi`:
```bash
sudo chown -R pi:pi /home/pi/speedtest-logger/
```

## Log Format

Each log entry contains:
```
2025-09-03 07:15:42 | Download: 45.23 Mbps | Upload: 12.45 Mbps | Ping: 15.2 ms | Server: Provider - City, CC | Tests averaged: 3
```

## Files Included

- `speedtest_logger.py` - Main Python application
- `speedtest-logger.service` - Systemd service file
- `install_service.sh` - Installation script
- `uninstall_service.sh` - Uninstallation script
- `README.md` - This documentation
