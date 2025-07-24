#!/bin/bash


# Create log directories if they don't exist
mkdir -p logs
mkdir -p reports/images

# Start SSH honeypot in background
echo "[+] Starting SSH honeypot..."
cd scripts
python3 ssh_honeypot.py > ../logs/ssh_honeypot.log 2>&1 &
SSH_PID=$!
echo $SSH_PID > ../logs/ssh_honeypot.pid

# Start Web honeypot in background
echo "[+] Starting Web honeypot..."
python3 web_honeypot.py > ../logs/web_honeypot.log 2>&1 &
WEB_PID=$!
echo $WEB_PID > ../logs/web_honeypot.pid

# Start FTP honeypot in background
echo "[+] Starting FTP honeypot..."
python3 ftp_honeypot.py > ../logs/ftp_honeypot.log 2>&1 &
FTP_PID=$!
echo $FTP_PID > ../logs/ftp_honeypot.pid

# Start Telnet honeypot in background
echo "[+] Starting Telnet honeypot..."
python3 telnet_honeypot.py > ../logs/telnet_honeypot.log 2>&1 &
TELNET_PID=$!
echo $TELNET_PID > ../logs/telnet_honeypot.pid

# Start Dashboard in background
echo "[+] Starting Dashboard..."
python3 dashboard.py > ../logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo $DASHBOARD_PID > ../logs/dashboard.pid

# Run geolocation processing
echo "[+] Processing geolocation data..."
python3 geolocation.py > ../logs/geolocation.log 2>&1

echo "[+] All honeypot services started!"
echo "[+] Dashboard available at: http://localhost:5000"
echo "[+] Web honeypot available at: http://localhost:8080"
echo "[+] SSH honeypot available at: localhost:2222"
echo "[+] FTP honeypot available at: localhost:2121"
echo "[+] Telnet honeypot available at: localhost:2323"
