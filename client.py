import socket
import sys

# Helper function for the client (similar function found in server.py)
def recv_line_client(s):
    """
    Reads a single line (up to a \n) from a socket.
    Returns the line *without* the \n.
    """
    message = b""
    while True:
        try:
            chunk = s.recv(1)
            if not chunk:
                # Server disconnected
                print("Server disconnected.")
                return None
            if chunk == b'\n':
                # End of the line
                return message
            message += chunk
        except ConnectionError:
            print("Connection lost.")
            return None



HOST = input("Enter server IP address: ")
PORT = 1337 
USERNAME = input("Enter your username: ")

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT} as {USERNAME}")
        
        sock.sendall(USERNAME.encode() + b'\n')
        
        while True:
            message = input(">> ")
            if not message:
                continue
            
            sock.sendall(message.encode() + b'\n')
            
            data = recv_line_client(sock)
            
            if data is None:
                break
                
            print(f"Received: {data.decode()!r}")

except KeyboardInterrupt:
    print("\nDisconnecting...")
except ConnectionRefusedError:
    print(f"Error: Connection refused. Is the server running on {HOST}:{PORT}?")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("Connection closed.")