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
if HOST == "":
    HOST = "127.0.0.1" # Fixed a small typo here from your last version
PORT = 1337 
USERNAME = input("Enter your username: ")

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT} as {USERNAME}")
        
        # 1. Send username
        sock.sendall(USERNAME.encode() + b'\n')

        # 2. Login - Wait for server's first response
        response_bytes = recv_line_client(sock)
        if response_bytes is None:
            print("Server closed connection during login.")
            sys.exit(1)
        
        response_str = response_bytes.decode()
        # Print the first thing server says (e.g. "Enter password:", "Welcome...", "ERROR...")
        print(response_str) 

        # 3. --- THIS IS THE UPDATED LOGIC ---
        
        if "Enter password:" in response_str:
            # --- PATH 1: Existing User ---
            password = input(">> ")
            sock.sendall(password.encode() + b'\n')
            
            # --- NEW FIX: ---
            # Wait for the server's *confirmation* message
            # (e.g., "Authenticated successfully." or an error)
            auth_response_bytes = recv_line_client(sock)
            
            if auth_response_bytes is None:
                # This happens if password was wrong and server just disconnected
                print("Login failed. Server disconnected.")
                sys.exit(1)
                
            # Print the confirmation (e.g., "Authenticated successfully.")
            auth_response_str = auth_response_bytes.decode()
            print(auth_response_str)
            
            # If the confirmation was an error, exit
            if "ERROR:" in auth_response_str:
                 sys.exit(1) # Quit
            
            # If we get here, login was successful, proceed to main loop.

        elif "registered" in response_str:
            # --- PATH 2: New User ---
            # We already printed the "Welcome..." message.
            # Nothing else to do, proceed to main loop.
            pass

        elif "ERROR:" in response_str:
            # --- PATH 3: Already Connected Error ---
            # We already printed the "ERROR..." message.
            # Just exit.
            sys.exit(1)
            
        else:
            # Unknown state
            print(f"Unknown server response: {response_str}")
            sys.exit(1)


        # 4. Send message loop
        # We only get here if login was successful.
        while True:
            message = input(">> ")
            if not message:
                continue
            
            sock.sendall(message.encode() + b'\n')
            
            data = recv_line_client(sock)
            
            if data is None:
                print("Connection closed by server.")
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