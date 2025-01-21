#!/bin/bash

# Print startup information
echo "=== Railway Startup Script ==="
echo "Current directory: $(pwd)"
echo "Files in directory: $(ls -la)"

# Ensure source file exists
if [ ! -f "Discord_Message_exporter.py" ]; then
    echo "ERROR: Discord_Message_exporter.py not found!"
    echo "Directory contents:"
    ls -la
    exit 1
fi

# Create app directory if it doesn't exist
if [ ! -d "/app" ]; then
    echo "Creating /app directory..."
    mkdir -p /app
fi

# Copy and set permissions
echo "Copying bot file..."
cp Discord_Message_exporter.py /app/
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to copy bot file!"
    exit 1
fi

echo "Setting permissions..."
chmod +x /app/Discord_Message_exporter.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to set permissions!"
    exit 1
fi

# Run the bot
echo "Starting bot..."
echo "==========================="
cd /app
python3 Discord_Message_exporter.py 