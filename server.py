import socket
import sys
from info import getServerHost

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind(getServerHost())
    server.listen(1)
    while True:
        conn, addr = server.accept()
        with conn:
            print("Connected by", addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                else:
                    print(f"Received from {addr[1]}: {data}")
                    if data == b"__EXIT__":
                        sys.exit(0)
                    
                conn.sendall(data)
