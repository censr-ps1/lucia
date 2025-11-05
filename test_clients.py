import socket
import threading
import time
import os
import sys

HOST = '127.0.0.1'
DEFAULT_PORT = int(os.environ.get('LUCIA_PORT', '1337'))
PORT = DEFAULT_PORT
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except Exception:
        pass

# Helper function for the client (similar function found in server.py)
def recv_line_client(s):
    message = b""
    while True:
        chunk = s.recv(1)
        if not chunk:
            return None
        if chunk == b'\n':
            return message
        message += chunk

def client_routine(username, message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            
            s.sendall(username.encode() + b'\n')
            
            s.sendall(message.encode() + b'\n')
            
            # Use the helper function to read the reply
            data = recv_line_client(s)
            print(f"{username} received: {data!r}")
            
    except Exception as e:
        print(f"{username} error: {e}")

if __name__ == '__main__':
    clients = [
        threading.Thread(target=client_routine, args=("alice", "hello from alice")),
        threading.Thread(target=client_routine, args=("bob", "hi from bob")),
    ]

    for c in clients:
        c.start()

    for c in clients:
        c.join()

    print("Test clients finished")