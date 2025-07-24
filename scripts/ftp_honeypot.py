#!/usr/bin/env python3
import socket
import threading
import datetime
import json
import os


if not os.path.exists("../logs"):
    os.makedirs("../logs")

FTP_PORT = 2121
BANNER = "220 FTP Server Ready\r\n"

def handle_client(client_socket, addr):
    client_ip = addr[0]
    client_port = addr[1]


    client_socket.send(BANNER.encode())

    username = None
    password = None

    try:
        while True:
            data = client_socket.recv(1024).decode().strip()
            if not data:
                break


            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "source_ip": client_ip,
                "source_port": client_port,
                "service": "ftp",
                "command": data
            }

            with open("../logs/ftp_commands.json", "a") as f:
                f.write(json.dumps(log_entry) + "\n")


            if data.startswith("USER"):
                username = data[5:]
                client_socket.send("331 Password required\r\n".encode())


            elif data.startswith("PASS"):
                password = data[5:]

                if username:
                    log_entry = {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "source_ip": client_ip,
                        "source_port": client_port,
                        "username": username,
                        "password": password,
                        "service": "ftp"
                    }

                    with open("../logs/auth_attempts.json", "a") as f:
                        f.write(json.dumps(log_entry) + "\n")

                    print(f"[+] FTP login attempt: {username}:{password} from {client_ip}")

                client_socket.send("530 Login incorrect\r\n".encode())


            else:
                client_socket.send("530 Please login with USER and PASS\r\n".encode())

    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind(('0.0.0.0', FTP_PORT))
    server.listen(5)

    print(f"[+] FTP honeypot listening on port {FTP_PORT}")

    try:
        while True:
            client, addr = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client, addr))
            client_handler.daemon = True
            client_handler.start()
    except KeyboardInterrupt:
        print("[!] Shutting down FTP honeypot")
    finally:
        server.close()

if __name__ == "__main__":
    main()
