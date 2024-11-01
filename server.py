import socket
import os
import threading

NUMBYTES = 1024


class Server:
    def __init__(self):
        self.ip_port = ("127.0.0.1", 12345)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.threads = {}
        self.keepAlive = True
        self.serverLoop()  # Open server

    # /dir
    def listDirectory(self, conn):
        filesList = os.listdir("server/")

        if len(filesList) == 0:
            conn.sendall(b"[41]")
        else:
            conn.sendall(b"[10]")
            conn.sendall("|".join(filesList).encode())
            conn.sendall(b"<EOF>")
        pass

    # /register
    def registerUser(self, conn, clientId, userName):
        # Get list of registered usernames
        listUsernames = [
            self.threads[user]["name"].lower()
            for user in self.threads
            if self.threads[user]["name"] != ""
        ]

        if userName.lower() not in listUsernames:
            self.threads[clientId]["name"] = userName
            conn.sendall(b"[10]")
        else:
            conn.sendall(b"[31]")
        pass

    # /get
    def sendFile(self, conn, fileName):
        if fileName not in os.listdir("server/"):
            conn.sendall(b"[61]")
            return
        else:
            conn.sendall(b"[10]")

        file = open(f"server/{fileName}", "rb")
        with file:
            print(f"Sending file: {fileName}")

            # Read and send file data
            while True:
                # read data from file in chunks
                data = file.read(NUMBYTES)
                # break if no more data to read
                if not data:
                    break
                # send chunk to client
                conn.sendall(data)
            # send end-of-file marker
            conn.sendall(b"<EOF>")

            print(f'"{fileName}" has been sent to the client.')
            file.close()

    # /store
    def receiveFile(self, conn, fileName):
        os.makedirs("server", exist_ok=True)  # Ensure the server directory exists
        file = open(f"server/{fileName}", "wb")

        with file:
            print(f"Receiving file: {fileName}")
            while True:
                data = conn.recv(NUMBYTES)
                if not data:
                    break
                if data.endswith(b"<EOF>"):  # Check for end-of-file marker
                    file.write(data[:-5])  # Write data excluding the marker
                    conn.sendall(b"[50]")  # acknowledge file received
                    break
                file.write(data)
        file.close()
        print(f'"{fileName}" has been received from the client.')

    def parseCommand(self, command, conn, clientId):
        args = command.split()

        # Convert command to lowercase if whatever reason the server doesn't echo the command in lowercase
        args[0] = args[0].lower()

        # Check if user is registering or is already registered
        if args[0] != "/register" and self.threads[clientId]["name"] == "":
            conn.sendall(b"[12]")
            return  # Exit function

        match args[0]:
            case "/dir":
                self.listDirectory(conn)
            case "/register":
                if len(args) == 2:
                    self.registerUser(conn, clientId, args[1])
            case "/store":
                if len(args) == 2:
                    self.receiveFile(conn, args[1])
            case "/get":
                if len(args) == 2:
                    self.sendFile(conn, args[1])
            case _:
                conn.sendall(b"Invalid command")

    def handleClient(self, conn, addr):
        clientId = f"{addr[0]}:{addr[1]}"
        print(f"Connected by {clientId}")

        # Receive data from the client
        while self.keepAlive:
            # For ease of identification
            # if client hasn't registered: print IP:PORT
            # if client registered: print username
            terminalAlias = clientId
            if self.threads[clientId]["name"] != "":
                terminalAlias = self.threads[clientId]["name"]

            try:
                data = conn.recv(NUMBYTES)
                if not data:
                    print(terminalAlias, "disconnected")
                    self.threads.pop(clientId)  # remove thread from list
                    break
                else:
                    print(f"{terminalAlias}: {data.decode()}")
                    self.parseCommand(data.decode(), conn, clientId)
            except ConnectionResetError:
                print(terminalAlias, "disconnected, connection reset")
                self.threads.pop(clientId)
                break
        pass

    def serverLoop(self):
        self.server.bind(self.ip_port)
        self.server.listen(1)

        print(f"\nServer is running on {self.ip_port[0]}:{self.ip_port[1]}\n")

        while self.keepAlive:
            # Accept connections from outside
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handleClient, args=(conn, addr))
            thread.start()
            self.threads[f"{addr[0]}:{addr[1]}"] = {"thread": thread, "name": ""}


if __name__ == "__main__":
    Server()
    pass
