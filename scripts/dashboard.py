#!/usr/bin/env python3

from flask import Flask, render_template_string, jsonify, request
import json
import os
import datetime

app = Flask(__name__)

def load_auth_attempts():
    attempts = []
    try:
        with open("../logs/auth_attempts.json", "r") as f:
            for line in f:
                try:
                    attempts.append(json.loads(line))
                except:
                    pass
    except FileNotFoundError:
        pass
    return attempts

def load_web_visits():
    visits = []
    try:
        with open("../logs/web_visits.json", "r") as f:
            for line in f:
                try:
                    visits.append(json.loads(line))
                except:
                    pass
    except FileNotFoundError:
        pass
    return visits

def load_geo_data():
    try:
        with open("../logs/geolocation.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Advanced Honeypot Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f0f0f0; }
        h1, h2 { color: #333; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background-color: white; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
        .stats { display: flex; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; }
        .stat-card { flex: 1; min-width: 150px; background-color: white; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); padding: 15px; margin: 0 10px 10px 0; text-align: center; }
        .stat-card h3 { margin-top: 0; color: #555; }
        .stat-card .number { font-size: 24px; font-weight: bold; color: #4CAF50; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 12px; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .refresh-btn { background-color: #4CAF50; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
        .refresh-btn:hover { background-color: #45a049; }
        .tabs { display: flex; margin-bottom: 20px; }
        .tab { padding: 10px 20px; background-color: #ddd; cursor: pointer; margin-right: 5px; border-radius: 5px 5px 0 0; }
        .tab.active { background-color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .world-map { width: 100%; height: 400px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 5px; }
        .map-marker { width: 10px; height: 10px; background-color: red; border-radius: 50%; position: absolute; transform: translate(-50%, -50%); }
        .map-container { position: relative; width: 100%; height: 400px; overflow: hidden; }
        .world-map-img { width: 100%; height: 100%; object-fit: cover; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Advanced Honeypot Dashboard</h1>
        <button class="refresh-btn" onclick="location.reload()">Refresh Data</button>

        <div class="tabs">
            <div class="tab active" onclick="showTab('overview')">Overview</div>
            <div class="tab" onclick="showTab('attacks')">Attack Details</div>
            <div class="tab" onclick="showTab('geo')">Geolocation</div>
            <div class="tab" onclick="showTab('services')">Services</div>
        </div>
        <div id="overview" class="tab-content active">
            <div class="stats">
                <div class="stat-card">
                    <h3>Total Attacks</h3>
                    <div class="number">{{ total_attacks }}</div>
                </div>
                <div class="stat-card">
                    <h3>Unique IPs</h3>
                    <div class="number">{{ unique_ips }}</div>
                </div>
                <div class="stat-card">
                    <h3>SSH Attacks</h3>
                    <div class="number">{{ ssh_attacks }}</div>
                </div>
                <div class="stat-card">
                    <h3>Web Attacks</h3>
                    <div class="number">{{ web_attacks }}</div>
                </div>
                <div class="stat-card">
                    <h3>FTP Attacks</h3>
                    <div class="number">{{ ftp_attacks }}</div>
                </div>
                <div class="stat-card">
                    <h3>Countries</h3>
                    <div class="number">{{ countries }}</div>
                </div>
            </div>
            <div class="card">
                <h2>Recent Authentication Attempts</h2>
                <table>
                    <tr>
                        <th>Time</th>
                        <th>Source IP</th>
                        <th>Location</th>
                        <th>Service</th>
                        <th>Username</th>
                        <th>Password</th>
                    </tr>
                    {% for attempt in recent_attempts %}
                    <tr>
                        <td>{{ attempt.timestamp }}</td>
                        <td>{{ attempt.source_ip }}</td>
                        <td>
                            {% if attempt.geo %}
                                {{ attempt.geo.city }}, {{ attempt.geo.country }}
                            {% else %}
                                Unknown
                            {% endif %}
                        </td>
                        <td>{{ attempt.service }}</td>
                        <td>{{ attempt.username }}</td>
                        <td>{{ attempt.password }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
        <div id="attacks" class="tab-content">
            <div class="card">
                <h2>Top Attacker IPs</h2>
                <table>
                    <tr>
                        <th>IP Address</th>
                        <th>Location</th>
                        <th>Attack Count</th>
                    </tr>
                    {% for ip, count in top_ips %}
                    <tr>
                        <td>{{ ip }}</td>
                        <td>
                            {% if ip in geo_data %}
                                {{ geo_data[ip].city }}, {{ geo_data[ip].country }}
                            {% else %}
                                Unknown
                            {% endif %}
                        </td>
                        <td>{{ count }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            <div class="card">
                <h2>Top Usernames</h2>
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
            <div class="card">
                <h2>Top Passwords</h2>
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
        <div id="geo" class="tab-content">
            <div class="card">
                <h2>Attacker Geolocation</h2>
                <div class="map-container">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg" class="world-map-img">
                    {% for ip, data in geo_data.items() %}
                    <div class="map-marker" style="left: calc({{ (data.lon + 180) / 360 * 100 }}%); top: calc({{ (90 - data.lat) / 180 * 100 }}%);" title="{{ ip }} - {{ data.city }}, {{ data.country }}"></div>
                    {% endfor %}
                </div>
            </div>

            <div class="card">
                <h2>Attacks by Country</h2>
                <table>
                    <tr>
                        <th>Country</th>
                        <th>Attack Count</th>
                    </tr>
                    {% for country, count in countries_count %}
                    <tr>
                        <td>{{ country }}</td>
                        <td>{{ count }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>

        <div id="services" class="tab-content">
            <div class="card">
                <h2>Service Status</h2>
                <table>
                    <tr>
                        <th>Service</th>
                        <th>Port</th>
                        <th>Status</th>
                        <th>Attack Count</th>
                    </tr>
                    <tr>
                        <td>SSH Honeypot</td>
                        <td>2222</td>
                        <td>{{ ssh_status }}</td>
                        <td>{{ ssh_attacks }}</td>
                    </tr>
                    <tr>
                        <td>Web Honeypot</td>
                        <td>8080</td>
                        <td>{{ web_status }}</td>
                        <td>{{ web_attacks }}</td>
                    </tr>
                    <tr>
                        <td>FTP Honeypot</td>
                        <td>2121</td>
                        <td>{{ ftp_status }}</td>
                        <td>{{ ftp_attacks }}</td>
                    </tr>
                </table>
            </div>

            <div class="card">
                <h2>Generate Report</h2>
                <p>Generate a comprehensive HTML report with all attack data and statistics.</p>
                <button class="refresh-btn" onclick="generateReport()">Generate Report</button>
                <div id="report-status"></div>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabId) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });

            // Remove active class from all tab buttons
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab
            document.getElementById(tabId).classList.add('active');

            // Add active class to clicked tab button
            document.querySelectorAll('.tab').forEach(tab => {
                if (tab.textContent.toLowerCase().includes(tabId)) {
                    tab.classList.add('active');
                }
            });
        }

        function generateReport() {
            document.getElementById('report-status').innerHTML = 'Generating report...';

            fetch('/generate_report')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('report-status').innerHTML = 
                            'Report generated successfully! <a href="/report" target="_blank">View Report</a>';
                    } else {
                        document.getElementById('report-status').innerHTML = 'Error generating report: ' + data.error;
                    }
                })
                .catch(error => {
                    document.getElementById('report-status').innerHTML = 'Error: ' + error;
                });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    auth_attempts = load_auth_attempts()
    web_visits = load_web_visits()
    geo_data = load_geo_data()


    total_attacks = len(auth_attempts)

    unique_ips = set()
    for attempt in auth_attempts:
        unique_ips.add(attempt.get('source_ip', ''))
    for visit in web_visits:
        unique_ips.add(visit.get('source_ip', ''))

    ssh_attacks = sum(1 for a in auth_attempts if a.get('service') == 'ssh')
    web_attacks = sum(1 for a in auth_attempts if a.get('service') == 'web_login')
    ftp_attacks = sum(1 for a in auth_attempts if a.get('service') == 'ftp')


    recent_attempts = sorted(auth_attempts, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]


    for attempt in recent_attempts:
        ip = attempt.get('source_ip', '')
        if ip in geo_data:
            attempt['geo'] = geo_data[ip]


    ip_counts = {}
    for attempt in auth_attempts:
        ip = attempt.get('source_ip', '')
        ip_counts[ip] = ip_counts.get(ip, 0) + 1

    top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    username_counts = {}
    for attempt in auth_attempts:
        username = attempt.get('username', '')
        if username:
            username_counts[username] = username_counts.get(username, 0) + 1

    top_usernames = sorted(username_counts.items(), key=lambda x: x[1], reverse=True)[:10]


    password_counts = {}
    for attempt in auth_attempts:
        password = attempt.get('password', '')
        if password:
            password_counts[password] = password_counts.get(password, 0) + 1

    top_passwords = sorted(password_counts.items(), key=lambda x: x[1], reverse=True)[:10]


    countries = {}
    for ip, data in geo_data.items():
        country = data.get('country', 'Unknown')
        countries[country] = countries.get(country, 0) + 1

    countries_count = sorted(countries.items(), key=lambda x: x[1], reverse=True)


    ssh_status = "Running" if os.path.exists("../logs/ssh_honeypot.pid") else "Stopped"
    web_status = "Running" if os.path.exists("../logs/web_honeypot.pid") else "Stopped"
    ftp_status = "Running" if os.path.exists("../logs/ftp_honeypot.pid") else "Stopped"

    return render_template_string(DASHBOARD_TEMPLATE, 
                                 total_attacks=total_attacks,
                                 unique_ips=len(unique_ips),
                                 ssh_attacks=ssh_attacks,
                                 web_attacks=web_attacks,
                                 ftp_attacks=ftp_attacks,
                                 countries=len(countries),
                                 recent_attempts=recent_attempts,
                                 top_ips=top_ips,
                                 top_usernames=top_usernames,
                                 top_passwords=top_passwords,
                                 geo_data=geo_data,
                                 countries_count=countries_count,
                                 ssh_status=ssh_status,
                                 web_status=web_status,
                                 ftp_status=ftp_status)

@app.route('/generate_report')
def generate_report():
    try:

        os.system('python3 generate_report.py')
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/report')
def view_report():
    try:
        with open("../reports/honeypot_report.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Report not found. Please generate a report first."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
