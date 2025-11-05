# lucia
A privacy focused encrypted communicaton platform built in python using PGP to encrypt/decrypt messages. Orginally made as a final project for a Python Scripting class. It gets it's name from the Saint Lucia Racer (most endangered snake in the world). 

## What/How?

The purpose of this program is to provide a secure communication experience for users such that if the server was compromised no user messages or data would be available to the attacker. To provide this encryption and decryption will be handled on the client side. 

The client.py file will do the following for egress communication: 
1.	Check what user the current message is being sent to  
2.	Get that user’s PUBLIC PGP key
3.	When the message is sent, encrypt the text using the public key
4.	Send that encrypted message to the server which the server will then send to the receiver of the message.

The client.py file will do the following to handle ingress communication:

1.	The client will receive the message from the server
2.	The client will decrypt the message using the private key
3.	The client will display the decrypted message without the server ever seeing the true message.

Hypothetically with proper key management on the part of the users this method of communication is completely private even if the server handling messages becomes compromised.


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

Big thanks to the people below their code was a big help
    https://github.com/inforkgodara/python-chat-application/blob/master/README.md

# TODO

These are the things that still needed to be added

## Tasks

Basic Functionality

- [ ] Setup server so it only forwards messages between users
- [ ] Add encryption funcionality with PGP
- [ ] Make it look sexy


