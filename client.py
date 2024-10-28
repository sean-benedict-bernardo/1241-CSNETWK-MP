# Client application for the server application
import socket
import webbrowser
import os

"""
CLI prettifier
"""


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
        print(
            f"{CLI.FAIL+CLI.BOLD}ERROR: {CLI.ENDC+CLI.FAIL} {error_message} {CLI.ENDC}"
        )

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

    def __init__(self) -> None:
        os.system("cls")
        print(
            f"{CLI.HEADER+CLI.BOLD}Good Day{CLI.ENDC}\n"
            + "To get started, type /? to see the list of commands\n"
        )

        while self.proceed:
            str_input = input()
            self.handleInput(str_input)

    def hasConnection(self):
        return self.connection is not None

    def establishConnection(self, ip, address):
        try:
            # throw exception if connection already exists
            if self.hasConnection():
                raise ExistingConnectionException()
            
            # convert port number to integer
            address = int(address)

            # setup socekt
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # establish connection
            self.connection.connect((ip, address))
            CLI.printSuccess("Connection to the File Exchange Server is successful!")
        except ConnectionRefusedError:
            CLI.printError(
                "Connection to the Server has failed! Please check IP Address and Port Number."
            )
            self.connection = None
        except ExistingConnectionException:
            CLI.printError("Connection already exists. Please disconnect first.")
        pass

    def closeConnection(self):
        if self.hasConnection():
            self.connection.close()
            self.connection = None
            CLI.printSuccess("Disconnected from the server.")
        else:
            CLI.printError("Disconnection failed. Please connect to the server first.")

        pass

    def getDirectory(self):
        if self.hasConnection():
            self.connection.send(b"/dir")

            data = self.connection.recv(4096)

            if data:
                fileList = data.decode().split("|")
                print(f"{CLI.OKCYAN}Files in the server directory:{CLI.ENDC}")
                for file in fileList:
                    print(f"{CLI.OKCYAN}>{CLI.ENDC} {file}")
            else:
                CLI.printError("Failed to retrieve directory listing.")
        else:
            CLI.printError("No connection to the server. Please connect first.")

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

        command = command.split(" ")
        command[0] = command[0].lower()

        print()

        match command[0]:
            case "/?":
                self.printCommands()
            case "/join" | "/connect":
                if len(command) >= 3: self.establishConnection(command[1], command[2])
                else: CLI.printError("Invalid command. Please provide IP Address and Port Number")
            case "/leave" | "/disconnect":
                self.closeConnection()
            case "/dir":
                self.getDirectory()
            case "/get":
                # fetch file
                pass
            case "/quit":
                # close existing connections
                if self.hasConnection():
                    self.closeConnection()
                print("Quitting the application...")
                self.proceed = False
            case "/whatthesigma":
                # do not question this lmao
                webbrowser.open("https://www.youtube.com/watch?v=xvFZjo5PgG0")

            case "/killserver":
                # kill the server
                self.connection.send(b"/killserver")
                self.closeConnection()
                pass
            case _:
                CLI.printError("Invalid command")

        print()


if __name__ == "__main__":
    client = Client()
