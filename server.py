import socket
import os


class Server:
    def __init__(self):
        self.ip_port = ("127.0.0.1", 12345)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.users = []
        self.keepAlive = True
        self.serverLoop()  # Open server

    # /dir
    def listDirectory(self, conn):
        filesList = os.listdir("server/")
        msg = "|".join(filesList)
        conn.send(msg.encode())
        pass

    # /register
    def registerUser(self, conn, userName):
        if userName not in self.users:
            self.users.append(userName)
            conn.send(f"User {userName} has been registered".encode())
        else:
            conn.send(b"Error: Registration failed. Handle or alias already exists.")
        pass

    # /get
    def sendFile(self, conn, fileName):
        if fileName not in os.listdir("server/"):
            conn.send(b"File does not exist")
            return

        with open(f"server/{fileName}", "rb") as file:
            print(f"Sending file: {fileName}")
            while True:
                data = file.read(1024)
                if not data:
                    break
                conn.send(data)
            conn.send(b"<EOF>")  # Send end-of-file marker
            print(f"File {fileName} has been sent to the client.")

    # /store
    def receiveFile(self, conn, fileName):
        os.makedirs("server", exist_ok=True)  # Ensure the server directory exists
        with open(f"server/{fileName}", "wb") as file:
            print(f"Receiving file: {fileName}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                if data.endswith(b"<EOF>"):  # Check for end-of-file marker
                    file.write(data[:-5])  # Write data excluding the marker
                    break
                file.write(data)

    def parseCommand(self, command, conn):
            """
            /leave
            /register
            /store
            /dir
            /get
            /quit
            """
            args = command.split()

            match args[0]:
                case "/dir" | "/ls":
                    self.listDirectory(conn)
                case "/register":
                    if len(args) >= 2:
                        self.registerUser(conn, args[1])
                    else:
                        conn.send(b"Invalid command")
                case "/store":
                    if len(args) >= 2:
                        self.receiveFile(conn, args[1])
                    else:
                        conn.send(b"Invalid command")
                case "/get":
                    if len(args) >= 2:
                        self.sendFile(conn, args[1])
                    else:
                        conn.send(b"Invalid command")
                case "/killserver":
                    conn.send(b"Server is shutting down")
                    self.keepAlive = False
                case _:
                    conn.send(b"Invalid command")

    def serverLoop(self):
        self.server.bind(self.ip_port)
        self.server.listen(1)

        print(f"\nServer is running on {self.ip_port[0]}:{self.ip_port[1]}\n")

        while self.keepAlive:
            # Accept connections from outside
            conn, addr = self.server.accept()
            with conn:
                print(f"Connected by {addr[0]}:{addr[1]}")

                # Receive data from the client
                while self.keepAlive:
                    try:
                        data = conn.recv(1024)
                        if not data:
                            break
                        else:
                            print(f"{addr[1]}: {data.decode()}")
                            self.parseCommand(data.decode(), conn)

                    except Exception as err:
                        print(f"Error: {err}")
                        if type(err).__name__ == "ConnectionResetError":
                            print(f"Connection reset by {addr[1]}")
                        break


if __name__ == "__main__":
    Server()
    pass