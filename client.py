import socket

HOST = "127.0.0.1"
PORT = 1337

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    message = input("Enter a message to send: ").encode()
    sock.sendall(message)
    data = sock.recv(1024)

print(f"Received {data!r}")