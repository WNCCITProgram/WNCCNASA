#!/bin/bash
# Speedtest Logger Service Installation Script for Raspberry Pi
# Author: William A Loring
# Date: 09/03/25
# Updated to use speedtest_service.py wrapper

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="speedtest-service"
SERVICE_FILE="${SERVICE_NAME}.service"
INSTALL_DIR="/home/pi/speedtest-logger"
PYTHON_LOGGER="speedtest_logger.py"
PYTHON_SERVICE="speedtest_service.py"

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Speedtest Logger Service Installer    ${NC}"
echo -e "${BLUE}  (Using Service Wrapper)               ${NC}"
echo -e "${BLUE}==========================================${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root!${NC}"
   echo -e "${YELLOW}Please run as: ./install_service_wrapper.sh${NC}"
   exit 1
fi

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}Error: $SERVICE_FILE not found in current directory${NC}"
    exit 1
fi

# Check if Python files exist
if [ ! -f "$PYTHON_LOGGER" ]; then
    echo -e "${RED}Error: $PYTHON_LOGGER not found in current directory${NC}"
    exit 1
fi

if [ ! -f "$PYTHON_SERVICE" ]; then
    echo -e "${RED}Error: $PYTHON_SERVICE not found in current directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Installing Python dependencies...${NC}"
# Install required Python packages
pip3 install speedtest-cli rich schedule --user

echo -e "${YELLOW}Creating installation directory...${NC}"
# Create installation directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
    echo -e "${GREEN}Created directory: $INSTALL_DIR${NC}"
fi

echo -e "${YELLOW}Copying files...${NC}"
# Copy Python scripts to installation directory
cp "$PYTHON_LOGGER" "$INSTALL_DIR/"
cp "$PYTHON_SERVICE" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/$PYTHON_LOGGER"
chmod +x "$INSTALL_DIR/$PYTHON_SERVICE"
echo -e "${GREEN}Copied Python files to $INSTALL_DIR${NC}"

# Stop existing service if running
if sudo systemctl is-active --quiet "speedtest-logger" 2>/dev/null; then
    echo -e "${YELLOW}Stopping existing speedtest-logger service...${NC}"
    sudo systemctl stop speedtest-logger
    sudo systemctl disable speedtest-logger 2>/dev/null || true
fi

echo -e "${YELLOW}Installing systemd service...${NC}"
# Copy service file to systemd directory (requires sudo)
sudo cp "$SERVICE_FILE" /etc/systemd/system/
echo -e "${GREEN}Service file installed to /etc/systemd/system/${NC}"

# Reload systemd daemon
echo -e "${YELLOW}Reloading systemd daemon...${NC}"
sudo systemctl daemon-reload

# Enable the service
echo -e "${YELLOW}Enabling service...${NC}"
sudo systemctl enable "$SERVICE_NAME"

# Start the service
echo -e "${YELLOW}Starting service...${NC}"
sudo systemctl start "$SERVICE_NAME"

# Check service status
sleep 3
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✓ Service is running successfully!${NC}"
    
    # Show initial log output
    echo -e "${YELLOW}Initial service output:${NC}"
    sudo journalctl -u "$SERVICE_NAME" --no-pager -n 10
else
    echo -e "${RED}✗ Service failed to start. Check logs with:${NC}"
    echo -e "${YELLOW}sudo journalctl -u $SERVICE_NAME -f${NC}"
    
    # Show error logs
    echo -e "${RED}Recent error logs:${NC}"
    sudo journalctl -u "$SERVICE_NAME" --no-pager -n 20
fi

echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}Installation completed!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  Status:  ${BLUE}sudo systemctl status $SERVICE_NAME${NC}"
echo -e "  Start:   ${BLUE}sudo systemctl start $SERVICE_NAME${NC}"
echo -e "  Stop:    ${BLUE}sudo systemctl stop $SERVICE_NAME${NC}"
echo -e "  Restart: ${BLUE}sudo systemctl restart $SERVICE_NAME${NC}"
echo -e "  Reload:  ${BLUE}sudo systemctl reload $SERVICE_NAME${NC}"
echo -e "  Logs:    ${BLUE}sudo journalctl -u $SERVICE_NAME -f${NC}"
echo -e "  Disable: ${BLUE}sudo systemctl disable $SERVICE_NAME${NC}"
echo
echo -e "${GREEN}Log files will be created in: $INSTALL_DIR${NC}"
echo -e "${YELLOW}Service will start automatically on boot.${NC}"
echo -e "${BLUE}The service wrapper provides better error handling and graceful shutdown.${NC}"
