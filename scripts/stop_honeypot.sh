#!/bin/bash

echo "[+] Stopping honeypot services..."

# Stop SSH honeypot
if [ -f logs/ssh_honeypot.pid ]; then
    PID=$(cat logs/ssh_honeypot.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "[+] SSH honeypot stopped."
    else
        echo "[!] SSH honeypot not running."
    fi
    rm logs/ssh_honeypot.pid
fi

# Stop Web honeypot
if [ -f logs/web_honeypot.pid ]; then
    PID=$(cat logs/web_honeypot.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "[+] Web honeypot stopped."
    else
        echo "[!] Web honeypot not running."
    fi
    rm logs/web_honeypot.pid
fi

# Stop FTP honeypot
if [ -f logs/ftp_honeypot.pid ]; then
    PID=$(cat logs/ftp_honeypot.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "[+] FTP honeypot stopped."
    else
        echo "[!] FTP honeypot not running."
    fi
    rm logs/ftp_honeypot.pid
fi
# Stop Telnet honeypot
if [ -f logs/telnet_honeypot.pid ]; then
    PID=$(cat logs/telnet_honeypot.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "[+] Telnet honeypot stopped."
    else
        echo "[!] Telnet honeypot not running."
    fi
    rm logs/telnet_honeypot.pid
fi
# Stop Dashboard
if [ -f logs/dashboard.pid ]; then
    PID=$(cat logs/dashboard.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "[+] Dashboard stopped."
    else
        echo "[!] Dashboard not running."
    fi
    rm logs/dashboard.pid
fi

echo "[+] All honeypot services stopped!"
