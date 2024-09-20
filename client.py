# Client application for the server application
import socket
import sys
import webbrowser
from info import getServerHost

HOST, PORT = getServerHost()


class Client:
    connection = None

    def __init__(self) -> None:
        print("Good Day\nTo get started, type /? to see the list of commands")

        while True:
            str_input = input()

            if self.handleInput(str_input) == False:
                break

    def printCommands():
        print(
            """
List of Commands:
/join <server_ip_add> <port>    - Connect to the server application
/leave                          - Disconnect from the server application  
/dir                            - Request directory file list from a server
/get <file_name>                - Fetch a file from server
/quit                           - Quit the application
            """
        )

    def handleInput(self, command=None):
        command = command.split(" ")

        match command[0]:
            case "/?":
                self.printCommands()
            case "/join":
                # do error checking here
                pass
            case "/leave":
                # call leave, error checking here also
                print("Disconnecting from server")
            case "/dir":
                # call directory
                print("Requesting directory file list from server")
                pass
            case "/get":
                # do error checking here
                pass
            case "/quit":
                print("Quitting the application")
                return False
            case "/whatthesigma":
                # do not question this lmao
                webbrowser.open("https://www.youtube.com/watch?v=xvFZjo5PgG0")
            case _:
                print("Invalid command")


if __name__ == "__main__":
    client = Client()
