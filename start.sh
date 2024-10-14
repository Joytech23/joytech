#!/usr/bin/env bash

# Update package lists and install missing dependencies
apt-get update && apt-get install -y \
    gstreamer1.0-gl \
    gstreamer1.0-plugins-bad \
    enchant-2 \
    libsecret-1-0 \
    libmanette-0.2-0 \
    libgles2-mesa

# Install Chromium for Playwright
playwright install chromium

# Start the Flask app
gunicorn --bind 0.0.0.0:5000 app:app 

