#!/bin/bash
# Speedtest Logger Service Status Checker for Raspberry Pi
# Author: William A Loring
# Date: 09/03/25

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVICE_NAME="speedtest-logger"
INSTALL_DIR="/home/pi/speedtest-logger"

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}    Speedtest Logger Service Status     ${NC}"
echo -e "${BLUE}==========================================${NC}"

# Check if service is installed
if ! sudo systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
    echo -e "${RED}❌ Service is not installed${NC}"
    echo -e "${YELLOW}Run ./install_service.sh to install${NC}"
    exit 1
fi

# Check service status
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✅ Service is running${NC}"
    STATUS="active"
else
    echo -e "${RED}❌ Service is not running${NC}"
    STATUS="inactive"
fi

# Check if service is enabled
if sudo systemctl is-enabled --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✅ Service is enabled (starts on boot)${NC}"
else
    echo -e "${YELLOW}⚠️  Service is disabled (won't start on boot)${NC}"
fi

# Show service details
echo
echo -e "${BLUE}Service Details:${NC}"
sudo systemctl status "$SERVICE_NAME" --no-pager -l

# Show recent logs
echo
echo -e "${BLUE}Recent Logs (last 10 lines):${NC}"
sudo journalctl -u "$SERVICE_NAME" -n 10 --no-pager

# Check log files
echo
echo -e "${BLUE}Log Files:${NC}"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${GREEN}Installation directory: $INSTALL_DIR${NC}"
    if [ -f "$INSTALL_DIR/speedtest_log.txt" ]; then
        LOG_SIZE=$(du -h "$INSTALL_DIR/speedtest_log.txt" | cut -f1)
        LOG_LINES=$(wc -l < "$INSTALL_DIR/speedtest_log.txt")
        echo -e "${GREEN}Current log file: speedtest_log.txt (${LOG_SIZE}, ${LOG_LINES} entries)${NC}"
        
        echo -e "${YELLOW}Latest log entries:${NC}"
        tail -n 3 "$INSTALL_DIR/speedtest_log.txt" 2>/dev/null || echo -e "${YELLOW}No log entries yet${NC}"
    else
        echo -e "${YELLOW}No log file found yet${NC}"
    fi
    
    # List all log files
    LOG_FILES=$(find "$INSTALL_DIR" -name "speedtest_log.txt*" -type f | wc -l)
    if [ "$LOG_FILES" -gt 1 ]; then
        echo -e "${BLUE}Found $LOG_FILES log files (including rotated logs)${NC}"
    fi
else
    echo -e "${RED}Installation directory not found: $INSTALL_DIR${NC}"
fi

echo
echo -e "${BLUE}==========================================${NC}"
echo -e "${YELLOW}Quick Commands:${NC}"
echo -e "  View live logs: ${BLUE}sudo journalctl -u $SERVICE_NAME -f${NC}"
echo -e "  Restart service: ${BLUE}sudo systemctl restart $SERVICE_NAME${NC}"
echo -e "  Stop service: ${BLUE}sudo systemctl stop $SERVICE_NAME${NC}"
echo -e "  Start service: ${BLUE}sudo systemctl start $SERVICE_NAME${NC}"
