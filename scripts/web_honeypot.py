#!/usr/bin/env python3

from flask import Flask, request, render_template_string, redirect
import datetime
import json
import os


if not os.path.exists("../logs"):
    os.makedirs("../logs")

app = Flask(__name__)


LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>System Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f0f0; }
        .login-container { background-color: white; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); width: 300px; }
        h2 { text-align: center; color: #333; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; margin: 8px 0; box-sizing: border-box; border: 1px solid #ddd; border-radius: 4px; }
        input[type="submit"] { width: 100%; background-color: #4CAF50; color: white; padding: 10px; border: none; border-radius: 4px; cursor: pointer; }
        input[type="submit"]:hover { background-color: #45a049; }
        .error { color: red; text-align: center; }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Admin Login</h2>
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
        <form method="post" action="/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Login">
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def home():

    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "source_ip": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', ''),
        "path": request.path,
        "service": "web"
    }

    with open("../logs/web_visits.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"[+] Web visit from {request.remote_addr} to {request.path}")

    return render_template_string(LOGIN_PAGE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')


    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "source_ip": request.remote_addr,
        "username": username,
        "password": password,
        "user_agent": request.headers.get('User-Agent', ''),
        "service": "web_login"
    }
    with open("../logs/auth_attempts.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"[+] Web login attempt: {username}:{password} from {request.remote_addr}")


    return render_template_string(LOGIN_PAGE, error="Invalid username or password")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
