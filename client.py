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
    HOST = "127.0.0.1" # Default to localhost
PORT = 1337 
USERNAME = input("Enter your username: ")

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT} as {USERNAME}")
        
        # Send username to server
        sock.sendall(USERNAME.encode() + b'\n')

        # Login - Wait for server's first response
        response_bytes = recv_line_client(sock)
        if response_bytes is None:
            print("Server closed connection during login.")
            sys.exit(1)
        
        response_str = response_bytes.decode()
        # Print the first thing server says - could be prompt for password, welcome message, or error
        print(response_str) 
        
        if "Enter password:" in response_str:
            # If user is in the remote database, we need to send password
            password = input(">> ")
            sock.sendall(password.encode() + b'\n')
            
           
            # Wait for the server's *confirmation* message (e.g., "Authenticated successfully." or an error)
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
            # We already printed the "Welcome..." message.
            # TODO: Add shit (copilot thinks "shit" should be "support" what a dumbass) for private key
            pass

        elif "ERROR:" in response_str:
            # We already printed the "ERROR..." message.
            # Just exit.
            sys.exit(1)
            
        else:
            # Unknown state
            print(f"Unknown server response: {response_str}")
            sys.exit(1)

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