import socket
import os

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(("127.0.0.1", 12345))
        
        # with open("README.md", "rb") as file:
        #     data = file.read()
        #     client.sendall(data)

        client.sendall(b"/register Bob")

        data = client.recv(1024)
        if not data:
            return
        else:
            print(f"{data.decode()}")
        
        # client.sendall(b"/killserver")
        


        

if __name__ == "__main__":
    main()