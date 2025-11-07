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

# We use a set here so we don't have to worry about duplicate usernames
knownUsers = set()
# dict to map connected usernames to their conn object
connectedUsers = {}
# lock to synchronize access to user lists
user_lock = threading.Lock()

# Hardcoded password (temporary)
SECRET_PASSWORD = "a"
# At some point when I stop being lazy, this will be a randomly generated string that will be encrypted 

def recv_line(conn):
    # Reads a single line (up to a \n) from a socket.
    # Returns the line without the \n.
    message = b""
    while True:
        chunk = conn.recv(1)  # Read one byte at a time, this is used to solve some errors I was having
        if not chunk:
            # Client disconnected
            return None
        if chunk == b'\n':
            # End of the line
            return message
        message += chunk

def handle_client(conn, addr):
    # Handle a single client connection in its own thread.
    username = None # Define username
    authenticated = False # Flag to track if user was added to lists
    
    try:
        # Read the username
        username_bytes = recv_line(conn)
        if not username_bytes:
            print(f"Connection from {addr} closed before sending username")
            return
        
        username = username_bytes.decode()
        print(f"Connected by {addr} as {username}")

        with user_lock:
            if (username in knownUsers):
                
                # Check if user is already connected
                if username in connectedUsers:
                    print(f"{username} is already connected. Disconnecting new session.")
                    conn.sendall(b"ERROR: You are already connected elsewhere.\n")
                    return
                # Send password prompt
                conn.sendall(b"Enter password:\n")
                
                # Read password response
                password_bytes = recv_line(conn)
                if not password_bytes:
                    print(f"{username} ({addr}) disconnected before sending password")
                    return

                password = password_bytes.decode()

                # Check password
                if password != SECRET_PASSWORD:
                    print(f"Incorrect password '{password}' from {username} ({addr}). Disconnecting.")
                    return # Close connection by exiting thread
                

                print(f"{username} ({addr}) authenticated successfully.")
                # Add to connected users
                connectedUsers[username] = conn 
                authenticated = True # Mark as added to the list
                conn.sendall(b"Authenticated successfully.\n")
                
            else:
                # New user, add them
                print(f"New user: {username}. Adding to known users.")
                knownUsers.add(username) 
                connectedUsers[username] = conn 
                authenticated = True # Mark as added to the list
                # At some point, we will have them enter their private key here
                conn.sendall(f"Welcome, {username}! You are now registered.\n".encode())


        # Main message loop
        while True:
            # Use the helper to read just the message
            data = recv_line(conn)
            if data is None: # Handle client disconnect
                print(f"{username} ({addr}) disconnected")
                break
            message = data.decode()
            # Handle special commands
            if message == "/list":
                user_list = ""
                with user_lock:
                    # Create a comma-separated list of connected users
                    user_list = ", ".join(connectedUsers.keys())
                
                conn.sendall(f"Connected users: {user_list}\n".encode())
                continue
            
            print(f"Received {message!r} from {username}")
            
            # Send the reply back WITH a newline, so the client can read it
            conn.sendall(data + b'\n')
            
    except Exception as e:
        print(f"Error with {addr}: {e}")
    finally:
        # Only remove them if they were successfully authenticated and added
        if authenticated:
            with user_lock:
                # Check if they are still in the list before deleting
                if username in connectedUsers:
                    del connectedUsers[username]
                    print(f"Removed {username} from connected list.")
        
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