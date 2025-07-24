#!/usr/bin/env python3
import json
import datetime
import os
import matplotlib.pyplot as plt
from jinja2 import Template
import time

def load_logs(filename):
    """Load log entries from a file"""
    data = []
    try:
        with open(filename, "r") as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except:
                    pass
    except FileNotFoundError:
        pass
    return data

def load_geo_data():
    """Load geolocation data"""
    try:
        with open("../logs/geolocation.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def generate_time_chart(auth_attempts):
    """Generate chart showing attacks by hour of day"""
    # Count attacks by hour
    hours = [0] * 24
    for attempt in auth_attempts:
        try:
            timestamp = datetime.datetime.fromisoformat(attempt.get("timestamp", ""))
            hours[timestamp.hour] += 1
        except:
            pass

    # Create chart
    plt.figure(figsize=(10, 6))
    plt.bar(range(24), hours, color='#4CAF50')
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of Attacks')
    plt.title('Attack Distribution by Hour')
    plt.xticks(range(24))
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Ensure directory exists
    os.makedirs("../reports/images", exist_ok=True)

    # Save chart
    plt.savefig("../reports/images/time_distribution.png")
    plt.close()

    return hours

def generate_service_chart(auth_attempts):
    """Generate chart showing attacks by service"""
    # Count attacks by service
    services = {}
    for attempt in auth_attempts:
        service = attempt.get("service", "unknown")
        services[service] = services.get(service, 0) + 1
    # Create chart
    plt.figure(figsize=(8, 8))
    labels = list(services.keys())
    sizes = list(services.values())
    colors = ['#4CAF50', '#2196F3', '#FFC107', '#F44336', '#9C27B0']
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.axis('equal')
    plt.title('Attacks by Service')

    # Save chart
    plt.savefig("../reports/images/service_distribution.png")
    plt.close()

    return services

def generate_country_chart(geo_data):
    """Generate chart showing attacks by country"""
    # Count attacks by country
    countries = {}
    for ip, data in geo_data.items():
        country = data.get("country", "Unknown")
        countries[country] = countries.get(country, 0) + 1

    # Sort by count
    sorted_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)

    # Take top 10
    top_countries = sorted_countries[:10]

    # Create chart
    plt.figure(figsize=(10, 6))
    plt.bar([x[0] for x in top_countries], [x[1] for x in top_countries], color='#2196F3')
    plt.xlabel('Country')
    plt.ylabel('Number of Attackers')
    plt.title('Attackers by Country')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save chart
    plt.savefig("../reports/images/country_distribution.png")
    plt.close()

    return dict(top_countries)

def generate_html_report(auth_attempts, web_visits, geo_data):
    """Generate HTML report with all data and charts"""
    # Generate charts
    generate_time_chart(auth_attempts)
    generate_service_chart(auth_attempts)
    generate_country_chart(geo_data)

    # Calculate statistics
    total_attacks = len(auth_attempts)
    unique_ips = len(set(a.get("source_ip", "") for a in auth_attempts))

    # Count by service
    services = {}
    for attempt in auth_attempts:
        service = attempt.get("service", "unknown")
        services[service] = services.get(service, 0) + 1

    # Count usernames and passwords
    usernames = {}
    passwords = {}
    for attempt in auth_attempts:
        username = attempt.get("username", "")
        password = attempt.get("password", "")

        if username:
            usernames[username] = usernames.get(username, 0) + 1
        if password:
            passwords[password] = passwords.get(password, 0) + 1

    # Get top 10 usernames and passwords
    top_usernames = sorted(usernames.items(), key=lambda x: x[1], reverse=True)[:10]
    top_passwords = sorted(passwords.items(), key=lambda x: x[1], reverse=True)[:10]

    # Get recent attacks (last 20)
    recent_attacks = sorted(auth_attempts, key=lambda x: x.get("timestamp", ""), reverse=True)[:20]

    # Add geolocation data to recent attacks
    for attack in recent_attacks:
        ip = attack.get("source_ip", "")
        if ip in geo_data:
            attack["geo"] = geo_data[ip]

    # HTML template
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Honeypot Security Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; color: #333; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { background-color: #2c3e50; color: white; padding: 20px; margin-bottom: 20px; border-radius: 5px; }
            .section { margin-bottom: 30px; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            h1, h2, h3 { margin-top: 0; }
            .stats { display: flex; flex-wrap: wrap; justify-content: space-between; margin-bottom: 20px; }
            .stat-box { flex: 1; min-width: 200px; background-color: white; padding: 15px; margin: 10px; border-radius: 5px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .stat-box h3 { margin-top: 0; color: #2c3e50; }
            .stat-box p { font-size: 24px; font-weight: bold; margin: 10px 0; color: #4CAF50; }
            .chart-container { text-align: center; margin: 20px 0; }
            .chart-container img { max-width: 100%; height: auto; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #4CAF50; color: white; }
            tr:hover { background-color: #f5f5f5; }
            .footer { text-align: center; margin-top: 30px; padding: 20px; color: #777; }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <h1>Honeypot Security Report</h1>
                <p>Generated on {{ date }}</p>
            </div>
        </div>
        <div class="container">
            <div class="section">
                <h2>Executive Summary</h2>
                <div class="stats">
                    <div class="stat-box">
                        <h3>Total Attacks</h3>
                        <p>{{ total_attacks }}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Unique IPs</h3>
                        <p>{{ unique_ips }}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Countries</h3>
                        <p>{{ countries }}</p>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Attack Distribution</h2>
                <div class="chart-container">
                    <h3>Attacks by Service</h3>
                    <img src="images/service_distribution.png" alt="Service Distribution">
                </div>
                <div class="chart-container">
                    <h3>Attacks by Time of Day</h3>
                    <img src="images/time_distribution.png" alt="Time Distribution">
                </div>
                <div class="chart-container">
                    <h3>Attackers by Country</h3>
                    <img src="images/country_distribution.png" alt="Country Distribution">
                </div>
            </div>

            <div class="section">
                <h2>Top Attack Vectors</h2>
                <div style="display: flex; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 300px; margin-right: 20px;">
                        <h3>Top Usernames</h3>
                        <table>
                            <tr>
                                <th>Username</th>
                                <th>Count</th>
                            </tr>
                            {% for username, count in top_usernames %}
                            <tr>
                                <td>{{ username }}</td>
                                <td>{{ count }}</td>
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                    <div style="flex: 1; min-width: 300px;">
                        <h3>Top Passwords</h3>
                        <table>
                            <tr>
                                <th>Password</th>
                                <th>Count</th>
                            </tr>
                            {% for password, count in top_passwords %}
                            <tr>
                                <td>{{ password }}</td>
                                <td>{{ count }}</td>
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                </div>
            </div>
            <div class="section">
                <h2>Recent Attacks</h2>
                <table>
                    <tr>
                        <th>Time</th>
                        <th>Source IP</th>
                        <th>Location</th>
                        <th>Service</th>
                        <th>Username</th>
                        <th>Password</th>
                    </tr>
                    {% for attack in recent_attacks %}
                    <tr>
                        <td>{{ attack.timestamp }}</td>
                        <td>{{ attack.source_ip }}</td>
                        <td>
                            {% if attack.geo %}
                                {{ attack.geo.city }}, {{ attack.geo.country }}
                            {% else %}
                                Unknown
                            {% endif %}
                        </td>
                        <td>{{ attack.service }}</td>
                        <td>{{ attack.username }}</td>
                        <td>{{ attack.password }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>

            <div class="footer">
                <p>Generated by Kali Honeypot System</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Render template
    template = Template(template_str)
    html = template.render(
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_attacks=total_attacks,
        unique_ips=unique_ips,
        countries=len(set(data.get("country", "Unknown") for data in geo_data.values())),
        top_usernames=top_usernames,
        top_passwords=top_passwords,
        recent_attacks=recent_attacks
    )

    # Save HTML report
    with open("../reports/honeypot_report.html", "w") as f:
        f.write(html)

    print(f"[+] Report generated: ../reports/honeypot_report.html")

def main():
    print("[+] Generating honeypot report...")

    # Create reports directory if it doesn't exist
    os.makedirs("../reports", exist_ok=True)
    os.makedirs("../reports/images", exist_ok=True)

    # Load data
    auth_attempts = load_logs("../logs/auth_attempts.json")
    web_visits = load_logs("../logs/web_visits.json")
    geo_data = load_geo_data()

    # Generate report
    generate_html_report(auth_attempts, web_visits, geo_data)

if __name__ == "__main__":
    main()
