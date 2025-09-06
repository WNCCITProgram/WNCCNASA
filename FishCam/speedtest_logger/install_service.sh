#!/bin/bash
# Speedtest Logger Service Installation Script for Raspberry Pi
# Author: William A Loring
# Date: 09/03/25

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="speedtest-logger"
SERVICE_FILE="${SERVICE_NAME}.service"
INSTALL_DIR="/home/pi/speedtest-logger"
PYTHON_FILE="speedtest_logger.py"

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Speedtest Logger Service Installer    ${NC}"
echo -e "${BLUE}==========================================${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root!${NC}"
   echo -e "${YELLOW}Please run as: ./install_service.sh${NC}"
   exit 1
fi

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}Error: $SERVICE_FILE not found in current directory${NC}"
    exit 1
fi

# Check if Python file exists
if [ ! -f "$PYTHON_FILE" ]; then
    echo -e "${RED}Error: $PYTHON_FILE not found in current directory${NC}"
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
# Copy Python script to installation directory
cp "$PYTHON_FILE" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/$PYTHON_FILE"
echo -e "${GREEN}Copied $PYTHON_FILE to $INSTALL_DIR${NC}"

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
sleep 2
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✓ Service is running successfully!${NC}"
else
    echo -e "${RED}✗ Service failed to start. Check logs with:${NC}"
    echo -e "${YELLOW}sudo journalctl -u $SERVICE_NAME -f${NC}"
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
echo -e "  Logs:    ${BLUE}sudo journalctl -u $SERVICE_NAME -f${NC}"
echo -e "  Disable: ${BLUE}sudo systemctl disable $SERVICE_NAME${NC}"
echo
echo -e "${GREEN}Log files will be created in: $INSTALL_DIR${NC}"
echo -e "${YELLOW}Service will start automatically on boot.${NC}"
