# Raspberry Pi Speedtest Logger Service

## 📁 Complete Package Contents

### Core Files
- **`speedtest_logger.py`** - Main Python application that runs speed tests
- **`speedtest-logger.service`** - Systemd service configuration file
- **`README.md`** - Complete documentation

### Installation & Management Scripts
- **`install_service.sh`** - Automated installation script
- **`uninstall_service.sh`** - Complete removal script  
- **`check_service.sh`** - Service status and log checker

## 🚀 Quick Start Guide

### 1. Transfer Files to Raspberry Pi
```bash
# Copy all files to your Raspberry Pi
scp *.py *.sh *.service pi@your-pi-ip:~/speedtest-logger/
```

### 2. Install the Service
```bash
cd ~/speedtest-logger
chmod +x *.sh
./install_service.sh
```

### 3. Check Status
```bash
./check_service.sh
```

## 📊 What It Does

✅ **Automated Testing**: Runs every 30 minutes (configurable)  
✅ **Accurate Results**: Averages 3 tests per session  
✅ **Persistent Logging**: Daily rotating logs with 30-day retention  
✅ **Auto-Start**: Starts automatically on boot  
✅ **Rich Display**: Beautiful console output with colors and progress  
✅ **Error Handling**: Graceful handling of network failures  

## 📝 Log Format Example
```
2025-09-03 07:04:11 | Download: 424.96 Mbps | Upload: 326.23 Mbps | Ping: 11.3 ms | Server: Xbar7 Communications - Lyons, CO, US | Tests averaged: 3
```

## ⚙️ Service Configuration

### Default Settings (in speedtest_logger.py)
```python
TEST_INTERVAL_MINUTES = 30  # Test frequency
NUM_RUNS_TO_AVERAGE = 3     # Tests per session
LOG_FILE_PATH = "speedtest_log.txt"  # Log filename
```

### Service Properties
- **User**: pi
- **Working Directory**: /home/pi/speedtest-logger
- **Restart Policy**: Always restart on failure
- **Dependencies**: Waits for network connectivity

## 🛠️ Management Commands

```bash
# Service Control
sudo systemctl start speedtest-logger
sudo systemctl stop speedtest-logger
sudo systemctl restart speedtest-logger
sudo systemctl status speedtest-logger

# View Logs
sudo journalctl -u speedtest-logger -f    # Live logs
sudo journalctl -u speedtest-logger -n 50 # Last 50 entries

# Check Service Status
./check_service.sh

# Complete Removal
./uninstall_service.sh
```

## 🔧 Troubleshooting

### Common Issues
1. **Service fails to start**: Check network connectivity
2. **Permission errors**: Ensure files owned by pi user
3. **Python dependencies missing**: Run install script again

### Debug Commands
```bash
# Check service status
systemctl status speedtest-logger

# View detailed logs  
journalctl -u speedtest-logger --no-pager -l

# Test Python script manually
cd /home/pi/speedtest-logger
python3 speedtest_logger.py
```

## 📈 Performance Data

The service provides comprehensive internet performance monitoring:
- **Download speeds** in Mbps
- **Upload speeds** in Mbps  
- **Latency/ping** in milliseconds
- **Server information** (ISP, location)
- **Test reliability** (number of successful tests averaged)

Perfect for monitoring ISP performance over time and identifying connectivity issues!

---
*Created by William A Loring - Internet Speed Test Logger v1.0*
