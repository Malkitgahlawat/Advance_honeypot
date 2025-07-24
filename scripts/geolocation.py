#!/usr/bin/env python3
import json
import requests
import os
import time

def get_ip_location(ip):
    """Get geolocation data for an IP address using ip-api.com"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        if data["status"] == "success":
            return {
                "country": data["country"],
                "countryCode": data["countryCode"],
                "region": data["regionName"],
                "city": data["city"],
                "lat": data["lat"],
                "lon": data["lon"],
                "isp": data["isp"],
                "org": data["org"]
            }
    except Exception as e:
        print(f"[-] Error getting location for {ip}: {e}")
    return None

def process_ips():
    """Process all IPs from logs and get their geolocation"""
    # Create geolocation directory if it doesn't exist
    if not os.path.exists("../logs"):
        os.makedirs("../logs")

    # Get all unique IPs from logs
    ips = set()

    # Auth attempts
    try:
        with open("../logs/auth_attempts.json", "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    ip = data.get("source_ip")
                    if ip and ip != "127.0.0.1" and ip != "localhost":
                        ips.add(ip)
                except:
                    pass
    except FileNotFoundError:
        pass

    # Web visits
    try:
        with open("../logs/web_visits.json", "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    ip = data.get("source_ip")
                    if ip and ip != "127.0.0.1" and ip != "localhost":
                        ips.add(ip)
                except:
                    pass
    except FileNotFoundError:
        pass

    # FTP commands
    try:
        with open("../logs/ftp_commands.json", "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    ip = data.get("source_ip")
                    if ip and ip != "127.0.0.1" and ip != "localhost":
                        ips.add(ip)
                except:
                    pass
    except FileNotFoundError:
        pass

    # Get geolocation for each IP
    geo_data = {}
    for ip in ips:
        print(f"[+] Getting geolocation for {ip}")
        location = get_ip_location(ip)
        if location:
            geo_data[ip] = location
        time.sleep(1)  # Rate limiting to avoid API blocks

    # Save geolocation data
    with open(os.path.join(LOGS_DIR , 'geolocation.json'), "w") as f:
        json.dump(geo_data, f, indent=2)
    print(f"[+] Processed geolocation for {len(geo_data)} IPs")
    return geo_data

if __name__ == "__main__":
    process_ips()
