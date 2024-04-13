#!/bin/bash

# Ask user for the directory to save the plamp_service.config.json
read -p "Enter the directory where you want to save the plamp_service.config.json: " CONFIG_DIR

# Create the config and pictures directories if they do not exist
mkdir -p "$CONFIG_DIR"
PICTURE_DIR="$CONFIG_DIR/plamp_pics"
mkdir -p "$PICTURE_DIR"

# Define the full path of the config file
CONFIG_PATH="$CONFIG_DIR/plamp_service.config.json"

# Generate the config file with picture directory
echo "{
    \"interval_seconds\": 300,
    \"picture_directory\": \"$PICTURE_DIR\"
}" > "$CONFIG_PATH"

echo "Configuration file created at $CONFIG_PATH. You can change the picture directory in this file."

# Ask for the service running user with a default of the user who invoked sudo
DEFAULT_USER=${SUDO_USER:-$(whoami)}
read -p "Enter the username to run the Plamp service [$DEFAULT_USER]: " SERVICE_USER
SERVICE_USER=${SERVICE_USER:-$DEFAULT_USER}

# Define paths
INSTALL_DIR="/opt/plamp"
SCRIPT="plamp_service.py"
SERVICE_FILE="/etc/systemd/system/plamp_service.service"

# Create install directory
mkdir -p "$INSTALL_DIR"

# Copy script
cp "$SCRIPT" "$INSTALL_DIR"

# Update the script with the path to the config file
sed -i "s|'plamp_service.config.json'|'$CONFIG_PATH'|g" "$INSTALL_DIR/$SCRIPT"

# Set script permissions
chmod +x "$INSTALL_DIR/$SCRIPT"

# Create the systemd service file
echo "[Unit]
Description=Plamp Service

[Service]
ExecStart=/usr/bin/python3 $INSTALL_DIR/$SCRIPT
WorkingDirectory=$INSTALL_DIR
Restart=always
User=$SERVICE_USER

[Install]
WantedBy=multi-user.target" > "$SERVICE_FILE"

# Reload systemd and enable the service
systemctl daemon-reload
systemctl enable plamp_service
systemctl start plamp_service

echo "Plamp Service installed and started successfully."

