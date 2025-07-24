#!/bin/bash

echo "[+] Installing honeypot dependencies..."

# Update system
apt-get update
apt-get upgrade -y

# Install required packages
apt-get install -y python3 python3-pip git curl jq python3-matplotlib

# Install Python packages
echo "[+] Installing Python packages..."
pip3 install flask requests paramiko jinja2 numpy

# Try to install scikit-learn, but continue if it fails
pip3 install scikit-learn || echo "[!] scikit-learn installation failed, but continuing anyway"

echo "[+] Dependencies installed successfully!"
