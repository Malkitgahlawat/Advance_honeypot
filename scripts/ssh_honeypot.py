#!/usr/bin/env python3

import socket
import threading
import paramiko
import datetime
import json
import os

# Setup logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
KEY_PATH = os.path.join(CONFIG_DIR, 'server.key')

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)


try:
    HOST_KEY = paramiko.RSAKey(filename=KEY_PATH)
    print(f"[+] Loaded SSH key from {KEY_PATH}")
except Exception as e:
    print(f"[!] Error loading SSH key: {e}")
    print(f"[+] Generating new SSH key...")
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    HOST_KEY = paramiko.RSAKey.generate(2048)
    HOST_KEY.write_private_key_file(KEY_PATH)
    print(f"[+] New SSH key generated at {KEY_PATH}")

SSH_PORT = 2222

class SSHServer(paramiko.ServerInterface):
    def __init__(self, client_address):
        self.client_address = client_address
        self.event = threading.Event()

    def check_auth_password(self, username, password):

    	log_entry = {
        	"timestamp": datetime.datetime.now().isoformat(),
       		"source_ip": self.client_address[0],
        	"source_port": self.client_address[1],
        	"username": username,
        	"password": password,
        	"service": "ssh"
   	 }

    	log_file = os.path.join(LOGS_DIR, 'auth_attempts.json')
    	with open(log_file, "a") as f:
        	f.write(json.dumps(log_entry) + "\n")

    	print(f"[+] Login attempt: {username}:{password} from {self.client_address[0]}")


    	return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_request(self, kind, chanid):
        self.event.set()
        return paramiko.OPEN_SUCCEEDED

def handle_connection(client, addr):
    print(f"[+] Connection from: {addr[0]}:{addr[1]}")

    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(HOST_KEY)
        server = SSHServer(addr)
        transport.start_server(server=server)

        channel = transport.accept(20)
        if channel is None:
            print(f"[-] No channel from {addr[0]}")
            return

        server.event.wait(10)
        transport.close()

    except Exception as e:
        print(f"[-] Error: {e}")
        try:
            transport.close()
        except:
            pass

def main():

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', SSH_PORT))
        sock.listen(100)
        print(f"[+] SSH honeypot listening on port {SSH_PORT}...")

        while True:
            client, addr = sock.accept()
            thread = threading.Thread(target=handle_connection, args=(client, addr))
            thread.daemon = True
            thread.start()

    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        sock.close()
if __name__ == '__main__':
    main()
