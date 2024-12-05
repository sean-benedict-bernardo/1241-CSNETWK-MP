# File Exchange System

A simple file exchange system in partial fulfillment of CSNETWK, Term 1 AY 2024-25. This repository contains a client and a server.

<hr>

## Contributors:
- Sean Bernardo
- Kenzo De Vera

## Installation

1. `git clone https://github.com/sean-benedict-bernardo/1241-CSNETWK-MP.git`
2. `cd 1241-CSNETWK-MP`
3. `python server.py`
4. Open a new terminal and run `python client.py`

<hr>

## Procedures
Procedures outlined assume existing connection and registration (except for `/register`), exceptions otherwise are handled accordingly.
### Getting Directory List
1. Client sends command `/dir` to server and awaits response.
2. Server sends either `[10]` or `[41]` indicating server have or have no files, respectively.
3. If `[41]` is recieved, client will inform user that there are no files on server
4. If `[10]` is received, server will transmit file list separated by `|`.
5. Client will listen for file list until `<EOF>` is recieved

### Registering user
1. Client sends command `/register <handle>` to server and awaits response.
2. Server sends either `[10]` or `[41]` indicating that user registration is successful or `<handle>` is already taken

### Sending Files

1. Client sends command `/store <filename>` and awaits acknowledgement before proceeding.
2. Server sends acknowledgement and creates empty file with `filename`
3. Client sends file data to server, dividing in chunks of 1024
4. Server keeps writing until `<EOF>` is detected
5. Server sends acknowledgement response `[50]` to client

### Fetching Files

1. Client sends command `/get <filename>` and awaits acknowledgement before proceeding.
2. Server sends either `[10]` or `[61]` indicating that file exists or does not exist on server-side. Server will be sending file if it does exist.
3. If `[10]` is recieved, client continuously listens for file from server and writing until `<EOF>` is detected.

<hr>

## Server Response Format:
- Response Format: `[xx]` | RegEx equivalent: `\[\d\d\]`
- Protocols with `\*` are client-side errors, the number is not transmitted by server but documented for completeness.

### Consolidated Responses list
#### [1x] Standard Responses
- [10] Generic Success, can proceed
- [11]* No Active Connection
- [12] Client is not registered
#### [2x] /join
- [21]* Timeout
- [22]* Pre-existing connection
#### [3x] /register
- [31] Username Taken
#### [4x] /dir
- [41] No files on server
#### [5x] /store
- [50] File has been uploaded
- [51]* File does not exist on client
#### [6x] /get
- [61] File does not exist on server
