# Client application for the server application
import socket
import webbrowser
import sys
import os

"""
CLI prettifier
"""

DEBUGMODE = True
NUMBYTES = 1024


class CLI:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @staticmethod
    def printError(error_message):
        print(f"{CLI.FAIL+CLI.BOLD}ERROR: {CLI.ENDC+CLI.FAIL+error_message+CLI.ENDC}")

    @staticmethod
    def incorrectUsage(syntax):
        CLI.printError("Syntax Error")
        print(f"Usage: {syntax}")

    @staticmethod
    def printSuccess(message):
        print(f"{CLI.OKGREEN}{message}{CLI.ENDC}")


class ExistingConnectionException(Exception):
    pass


"""
Client class
"""


class Client:
    connection = None
    proceed = True

    def __init__(self, autoStart=False) -> None:
        print(
            f"{CLI.HEADER+CLI.BOLD}Good Day{CLI.ENDC}\n"
            + "To get started, type /? to see the list of commands\n"
        )

        self.userName = ""

        if autoStart:
            print("Auto-starting connection to server...")
            self.handleInput("/join 127.0.0.1 12345")

        while self.proceed:
            try:
                print(f"{self.userName}>", end=" ")
                str_input = input()
                self.handleInput(str_input)
            except KeyboardInterrupt:
                if not self.hasConnection():
                    self.handleInput("/quit")
                    break  # terminate the loop
                # nothing happens otherwise

    def hasConnection(self):
        return self.connection is not None

    def sendCommand(self, command):
        if not self.hasConnection():
            # [11]
            CLI.printError("No connection to the server. Please connect first.")
            return False
        try:
            # send command to server
            self.connection.sendall(command.encode())

            # await response from server
            response = self.connection.recv(NUMBYTES).decode()

            # check responses as defined in README.md
            match response:
                case "[10]":
                    return True
                case "[12]":
                    CLI.printError("Please register a handle first.")
                case "[31]":
                    CLI.printError("User handle already exists. Please choose another.")
                case "[41]":
                    print("Server directory is empty.")
                case "[61]":
                    CLI.printError("Requested file does not exist on the server.")
        except ConnectionResetError:
            CLI.printError("Connection to the server has been lost.")
            self.connection = None
            self.userName = ""

        return False

    # /join <server_ip_add> <port>
    def establishConnection(self, ip, address):
        try:
            # throw exception if connection already exists
            if self.hasConnection():
                raise ExistingConnectionException()

            # convert port number to integer
            address = int(address)

            # setup socekt
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # set timeout establish connection
            self.connection.settimeout(3)
            self.connection.connect((ip, address))
            self.connection.settimeout(None)
            CLI.printSuccess("Connection to the File Exchange Server is successful!")
        except ExistingConnectionException:
            # [22]
            CLI.printError("Connection already exists. Please disconnect first.")
        except:
            # [21]
            CLI.printError(
                "Connection to the Server has failed! Please check IP Address and Port Number."
            )
            self.connection = None
        pass

    # /register <handle>
    def registerUser(self, handle):
        if self.sendCommand(f"/register {handle}"):
            self.userName = handle
            CLI.printSuccess(f"User handle set to: {handle}!")

    # /leave
    def closeConnection(self):
        if self.hasConnection():
            self.connection.close()
            self.connection = None
            CLI.printSuccess("Disconnected from the server.")
            self.userName = ""
        else:
            CLI.printError("Disconnection failed. Please connect to the server first.")

    # /dir
    def getDirectory(self):
        if self.sendCommand("/dir"):
            fileList = ""

            while True:
                data = self.connection.recv(NUMBYTES)
                fileList += data.decode()
                if b"<EOF>" in data:  # Check for end-of-file marker
                    break

            # decode -> remove <EOF> -> split filenames
            fileList = fileList.replace("<EOF>", "").split("|")
            print(f"{CLI.OKCYAN}Files in the server directory:{CLI.ENDC}")
            for file in fileList:
                print(f"{CLI.OKCYAN}>{CLI.ENDC} {file}")

    # /store <filename>
    def sendFile(self, filename):
        if self.sendCommand(f"/store {filename}"):
            try:
                with open(f"client/{filename}", "rb") as file:
                    print(f"Sending file: {filename}")

                    # Read and send file data
                    while True:
                        data = file.read(NUMBYTES)
                        if not data:
                            break
                        self.connection.sendall(data)
                    # send end-of-file marker
                    self.connection.sendall(b"<EOF>")

                    file.close()

                # await [50] from server
                res = self.connection.recv(NUMBYTES).decode()
                if res == "[50]":
                    CLI.printSuccess(f"File {filename} has been sent to the server.")

            except FileNotFoundError:
                CLI.printError(f'"{filename}" does not exist')

    # /get <file_name>
    def getFile(self, filename):
        if self.sendCommand(f"/get {filename}"):
            print("Receiving file...")
            file = open(f"client/{filename}", "wb")

            with file:
                # await file data
                while True:
                    data = self.connection.recv(NUMBYTES)
                    if b"<EOF>" in data:  # Check for end-of-file marker
                        break
                    file.write(data)
                CLI.printSuccess(f"File received from server: {filename}")
                file.close()

    # /?
    def printCommands(self):
        def printCommand(command, description):
            print(f"{CLI.BOLD}%-32s{CLI.ENDC} : %s" % (command, description))
            pass

        print(f"{CLI.BOLD}{CLI.HEADER}List of Commands:{CLI.ENDC}")
        printCommand(
            "/join <server_ip_add> <port>", "Connect to the server application"
        )
        printCommand("/leave", "Disconnect from the server application")
        printCommand("/register <handle>", "Register a unique handle or alias")
        printCommand("/store <filename>", "Send a file to the server")
        printCommand("/dir", "Request directory file list from a server")
        printCommand("/get <file_name>", "Fetch a file from server")
        printCommand("/quit", "Quit the application")

    def handleInput(self, command=None):
        if command is None or command == "":
            CLI.printError("No Command Entered")
            self.proceed = True
            return

        # remove empty strings split command
        parsedCommand = list(filter(lambda x: x != "", command.split(" ")))
        parsedCommand[0] = parsedCommand[0].lower()

        print()
        """
        Note on conditions on number of arguments:
            The command will still be executed if it 
            contains more than the require number of arguments
            the excess arguments will be ignored
        """
        match parsedCommand[0]:
            case "/?":
                self.printCommands()
            case "/join" | "/connect":
                if len(parsedCommand) >= 3:
                    self.establishConnection(parsedCommand[1], parsedCommand[2])
                else:
                    CLI.incorrectUsage("/join <server_ip_add> <port>")
            case "/leave" | "/disconnect":
                self.closeConnection()
            case "/register":
                if len(parsedCommand) >= 2 and parsedCommand[1] != "":
                    self.registerUser(parsedCommand[1])
                else:
                    CLI.incorrectUsage("/register <handle>")
            case "/store":
                if len(parsedCommand) >= 2:
                    self.sendFile(parsedCommand[1])
                else:
                    CLI.incorrectUsage("/store <filename>")
            case "/dir":
                self.getDirectory()
                pass
            case "/get":
                if len(parsedCommand) >= 2:
                    self.getFile(parsedCommand[1])
                else:
                    CLI.incorrectUsage("/get <filename>")
            case "/quit":
                if not self.hasConnection() or DEBUGMODE:
                    print(f"{CLI.HEADER}Quitting the application...{CLI.ENDC}\n")
                    self.proceed = False
                    if DEBUGMODE:
                        self.closeConnection()
                else:
                    CLI.printError("Please disconnect from the server first.")
            case "/whatthesigma":
                # do not question this lmao
                webbrowser.open("https://www.youtube.com/watch?v=xvFZjo5PgG0")
            case "/killserver":
                # kill the server
                self.connection.sendall(b"/killserver")
                self.closeConnection()
                pass
            case _:
                CLI.printError("Command not recognized.")
                print("Type /? to see the list of commands.")
        print()


if __name__ == "__main__":
    # the argument here is for ez testing
    os.system("cls")
    client = Client(len(sys.argv) > 1 and sys.argv[1].lower() == "join")
