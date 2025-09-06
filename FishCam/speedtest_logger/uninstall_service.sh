#!/bin/bash
# Speedtest Logger Service Uninstallation Script for Raspberry Pi
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

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Speedtest Logger Service Uninstaller  ${NC}"
echo -e "${BLUE}==========================================${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root!${NC}"
   echo -e "${YELLOW}Please run as: ./uninstall_service.sh${NC}"
   exit 1
fi

# Check if service exists
if ! sudo systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
    echo -e "${YELLOW}Service $SERVICE_NAME is not installed.${NC}"
    exit 0
fi

echo -e "${YELLOW}Stopping service if running...${NC}"
# Stop the service if it's running
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    sudo systemctl stop "$SERVICE_NAME"
    echo -e "${GREEN}Service stopped.${NC}"
else
    echo -e "${YELLOW}Service was not running.${NC}"
fi

echo -e "${YELLOW}Disabling service...${NC}"
# Disable the service
sudo systemctl disable "$SERVICE_NAME"
echo -e "${GREEN}Service disabled.${NC}"

echo -e "${YELLOW}Removing service file...${NC}"
# Remove service file
if [ -f "/etc/systemd/system/$SERVICE_FILE" ]; then
    sudo rm "/etc/systemd/system/$SERVICE_FILE"
    echo -e "${GREEN}Service file removed.${NC}"
fi

echo -e "${YELLOW}Reloading systemd daemon...${NC}"
# Reload systemd daemon
sudo systemctl daemon-reload
sudo systemctl reset-failed

echo -e "${YELLOW}Do you want to remove the installation directory? [y/N]${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}Removing installation directory...${NC}"
        rm -rf "$INSTALL_DIR"
        echo -e "${GREEN}Installation directory removed.${NC}"
    else
        echo -e "${YELLOW}Installation directory doesn't exist.${NC}"
    fi
else
    echo -e "${YELLOW}Installation directory preserved at: $INSTALL_DIR${NC}"
    echo -e "${BLUE}Log files are still available in the directory.${NC}"
fi

echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}Uninstallation completed!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo
echo -e "${YELLOW}Note: Python packages (speedtest-cli, rich, schedule) were not removed.${NC}"
echo -e "${YELLOW}If you want to remove them, run:${NC}"
echo -e "${BLUE}pip3 uninstall speedtest-cli rich schedule${NC}"
