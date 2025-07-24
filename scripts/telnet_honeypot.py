#!/usr/bin/env python3
import socket
import threading
import datetime
import json
import os
import re


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
TELNET_PORT = 2323

def handle_client(client_socket, addr):
    client_ip = addr[0]
    client_port = addr[1]


    client_socket.send(b"\r\nLogin: ")

    username = ""
    password = ""
    login_stage = "username"

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break


            text = data.decode('ascii', errors='ignore').strip()
            text = re.sub(r'[\x00-\x1F\x7F]', '', text)

            if login_stage == "username":
                username = text
                client_socket.send(b"Password: ")
                login_stage = "password"
            elif login_stage == "password":
                password = text


                log_entry = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "source_ip": client_ip,
                    "source_port": client_port,
                    "username": username,
                    "password": password,
                    "service": "telnet"
                }

                with open(os.path.join(LOGS_DIR, 'auth_attempts.json'), "a") as f:
                    f.write(json.dumps(log_entry) + "\n")

                print(f"[+] Telnet login attempt: {username}:{password} from {client_ip}")

                client_socket.send(b"\r\nLogin incorrect\r\n")
                time.sleep(1) 
                client_socket.close()
                break
                login_stage="username"

    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind(('0.0.0.0', TELNET_PORT))
    server.listen(5)

    print(f"[+] Telnet honeypot listening on port {TELNET_PORT}")

    try:
        while True:
            client, addr = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client, addr))
            client_handler.daemon = True
            client_handler.start()
    except KeyboardInterrupt:
        print("[!] Shutting down Telnet honeypot")
    finally:
        server.close()

if __name__ == "__main__":
    main()
