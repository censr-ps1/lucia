import socket
import threading
import os
import sys

HOST = "127.0.0.1"
# Allow overriding the port via env var LUCIA_PORT or first CLI arg
DEFAULT_PORT = int(os.environ.get("LUCIA_PORT", "1337"))
PORT = DEFAULT_PORT
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except Exception:
        pass

def recv_line(conn):
    """
    Reads a single line (up to a \n) from a socket.
    Returns the line *without* the \n.
    """
    message = b""
    while True:
        chunk = conn.recv(1)  # Read one byte at a time
        if not chunk:
            # Client disconnected
            return None
        if chunk == b'\n':
            # End of the line
            return message
        message += chunk

def handle_client(conn, addr):
    """Handle a single client connection in its own thread."""
    try:
        # Use the new helper to read just the username
        username_bytes = recv_line(conn)
        if not username_bytes:
            print(f"Connection from {addr} closed before sending username")
            return
        
        username = username_bytes.decode()
        print(f"Connected by {addr} as {username}")

        while True:
            # Use the new helper to read just the message
            data = recv_line(conn)
            if data is None: # Handle client disconnect
                print(f"{username} ({addr}) disconnected")
                break
            
            print(f"Received {data!r} from {username}")
            
            # Send the reply back WITH a newline, so the client can read it
            conn.sendall(data + b'\n')
            
    except Exception as e:
        print(f"Error with {addr}: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Allow the socket to timeout so we can handle KeyboardInterrupt
        sock.settimeout(1.0)  
        
        sock.bind((HOST, PORT))
        sock.listen()
        print(f"Server listening on {HOST}:{PORT}")
        
        try:
            while True:
                try:
                    conn, addr = sock.accept()
                    
                    t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                    t.start()
                    
                except socket.timeout:

                    pass 

        except KeyboardInterrupt:
            print("Shutting down server")

if __name__ == '__main__':
    main()