#!/usr/bin/env python3

import json
import os
import sys
import datetime
from collections import Counter

def load_logs(log_file):
    entries = []
    try:
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    entries.append(json.loads(line.strip()))
                except:
                    pass
    except FileNotFoundError:
        print(f"[!] Log file not found: {log_file}")
    return entries

def load_geo_data():
    try:
        with open("../logs/geolocation.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def analyze_auth_attempts(entries, geo_data):
    print("\n=== Authentication Attempts Analysis ===\n")


    services = Counter(entry.get('service', 'unknown') for entry in entries)
    print("Attempts by Service:")
    for service, count in services.most_common():
        print(f"  {service}: {count}")


    ips = Counter(entry.get('source_ip', 'unknown') for entry in entries)
    print("\nTop 10 Source IPs:")
    for ip, count in ips.most_common(10):
        location = "Unknown"
        if ip in geo_data:
            location = f"{geo_data[ip].get('city', 'Unknown')}, {geo_data[ip].get('country', 'Unknown')}"
        print(f"  {ip} ({location}): {count}")


    usernames = Counter(entry.get('username', 'unknown') for entry in entries)
    print("\nTop 10 Usernames:")
    for username, count in usernames.most_common(10):
        print(f"  {username}: {count}")


    passwords = Counter(entry.get('password', 'unknown') for entry in entries)
    print("\nTop 10 Passwords:")
    for password, count in passwords.most_common(10):
        print(f"  {password}: {count}")


    combos = Counter((entry.get('username', 'unknown'), entry.get('password', 'unknown')) for entry in entries)
    print("\nTop 10 Username/Password Combinations:")
    for (username, password), count in combos.most_common(10):
        print(f"  {username}:{password} - {count}")


    countries = Counter()
    for entry in entries:
        ip = entry.get('source_ip', '')
        if ip in geo_data:
            country = geo_data[ip].get('country', 'Unknown')
            countries[country] += 1

    print("\nAttacks by Country:")
    for country, count in countries.most_common():
        print(f"  {country}: {count}")

def analyze_web_visits(entries, geo_data):
    print("\n=== Web Visits Analysis ===\n")


    ips = Counter(entry.get('source_ip', 'unknown') for entry in entries)
    print("Top 10 Source IPs:")
    for ip, count in ips.most_common(10):
        location = "Unknown"
        if ip in geo_data:
            location = f"{geo_data[ip].get('city', 'Unknown')}, {geo_data[ip].get('country', 'Unknown')}"
        print(f"  {ip} ({location}): {count}")


    paths = Counter(entry.get('path', 'unknown') for entry in entries)
    print("\nRequested Paths:")
    for path, count in paths.most_common():
        print(f"  {path}: {count}")


    agents = Counter(entry.get('user_agent', 'unknown') for entry in entries)
    print("\nTop 10 User Agents:")
    for agent, count in agents.most_common(10):
        print(f"  {agent}: {count}")

def analyze_ftp_commands(entries, geo_data):
    print("\n=== FTP Commands Analysis ===\n")


    ips = Counter(entry.get('source_ip', 'unknown') for entry in entries)
    print("Top 10 Source IPs:")
    for ip, count in ips.most_common(10):
        location = "Unknown"
        if ip in geo_data:
            location = f"{geo_data[ip].get('city', 'Unknown')}, {geo_data[ip].get('country', 'Unknown')}"
        print(f"  {ip} ({location}): {count}")


    commands = Counter(entry.get('command', 'unknown') for entry in entries)
    print("\nTop FTP Commands:")
    for command, count in commands.most_common():
        print(f"  {command}: {count}")

def main():
    print("=== Honeypot Log Analysis ===")

    auth_log = "../logs/auth_attempts.json"
    web_log = "../logs/web_visits.json"
    ftp_log = "../logs/ftp_commands.json"

    auth_entries = load_logs(auth_log)
    web_entries = load_logs(web_log)
    ftp_entries = load_logs(ftp_log)
    geo_data = load_geo_data()

    if auth_entries:
        analyze_auth_attempts(auth_entries, geo_data)
    else:
        print("[!] No authentication attempts found.")

    if web_entries:
        analyze_web_visits(web_entries, geo_data)
    else:
        print("[!] No web visits found.")

    if ftp_entries:
        analyze_ftp_commands(ftp_entries, geo_data)
    else:
        print("[!] No FTP commands found.")


    print("\n=== Overall Statistics ===\n")
    print(f"Total authentication attempts: {len(auth_entries)}")
    print(f"Total web visits: {len(web_entries)}")
    print(f"Total FTP commands: {len(ftp_entries)}")


    all_ips = set()
    for entry in auth_entries:
        all_ips.add(entry.get('source_ip', ''))
    for entry in web_entries:
        all_ips.add(entry.get('source_ip', ''))
    for entry in ftp_entries:
        all_ips.add(entry.get('source_ip', ''))

    print(f"Unique IP addresses: {len(all_ips)}")


    countries = set()
    for ip in all_ips:
        if ip in geo_data:
            countries.add(geo_data[ip].get('country', 'Unknown'))

    print(f"Countries detected: {len(countries)}")
    print(f"Countries: {', '.join(sorted(countries))}")

if __name__ == "__main__":
    main()
