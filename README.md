# File Exchange System

A simple file exchange system in partial fulfillment of CSNETWK, Term 1 AY 2024-25. This repository contains a client and a server

## Contributors:
- Sean Bernardo
- Kenzo De Vera

## Server Response Format:
Response Format: `[xx]` | RegEx equivalent: `\[\d\d\]`

### [1x] Standard Responses
- [10] Generic Success, can proceed
- [11]* No Active Connection
- [12] Client is not registered
### [2x] /join
- [21]* Timeout
- [22]* Pre-existing connection
### [3x] /register
- [31] Username Taken
### [4x] /dir
- [41] No files on server
### [5x] /store
- [50] File has been uploaded
- [51]* File does not exist on client
### [6x] /get
- [61] File does not exist on server

\* Client-side error, number unused but documented for completeness