#!/bin/bash

# Uninstall the enviroplusweb systemd service
SERVICE_FILE="web_stream.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_FILE"

echo "Stopping $SERVICE_FILE..."
sudo systemctl stop "$SERVICE_FILE"

echo "Disabling $SERVICE_FILE..."
sudo systemctl disable "$SERVICE_FILE"

echo "Removing $SERVICE_PATH..."
sudo rm -f "$SERVICE_PATH"

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Service uninstalled."
