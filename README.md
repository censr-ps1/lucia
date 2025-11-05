# lucia
A privacy focused encrypted communicaton platform built in python using PGP to encrypt/decrypt messages. Orginally made as a final project for a Python Scripting class. It gets it's name from the Saint Lucia Racer (most endangered snake in the world). 

## How to use lucia

The repository contains a minimal server and client example. The server has been updated to accept multiple clients concurrently using threads. To try it locally:

1. Start the server (runs until Ctrl+C):

	python "c:\\Users\\user\\Visual Studio Code Projects\\lucia\\server.py"

2. In another terminal, run the interactive client or use the included test script:

	python "c:\\Users\\user\\Visual Studio Code Projects\\lucia\\client.py"

	or (non-interactive test):

	python "c:\\Users\\user\\Visual Studio Code Projects\\lucia\\test_clients.py"

The `test_clients.py` script launches two simulated clients that send a message and print the echoed response.

## References

### Big thanks to the people below
https://github.com/inforkgodara/python-chat-application/blob/master/README.md
