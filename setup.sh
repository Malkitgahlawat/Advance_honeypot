#!/bin/bash

echo "===== Kali Linux Advanced Honeypot Setup ====="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "[!] Please run as root"
  exit 1
fi

# Check if running on Kali
if ! grep -q "Kali" /etc/os-release; then
  echo "[!] Warning: This script is designed for Kali Linux"
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

echo "[+] Installing dependencies..."
bash scripts/install_dependencies.sh

# Create SSH key for honeypot
if [ ! -f config/server.key ]; then
  echo "[+] Generating SSH server key..."
  mkdir -p config
  ssh-keygen -t rsa -b 2048 -f config/server.key -N ""
fi

echo "[+] Setup complete!"
echo
echo "To start the honeypot:"
echo "  sudo ./scripts/start_honeypot.sh"
echo
echo "To stop the honeypot:"
echo "  sudo ./scripts/stop_honeypot.sh"
echo
echo "To analyze collected data:"
echo "  python3 scripts/analyze_logs.py"
echo
echo "To generate a report:"
echo "  python3 scripts/generate_report.py"
echo
echo "Dashboard will be available at: http://localhost:5000"
