import socket
import sys
import threading
from colors import cprint, print_error, print_info, print_success, print_warning, print_received, get_prompt, cstr

# Global state
current_conversation = None
active_conversation_lock = threading.Lock()
sock = None
should_exit = False

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
                return None
            if chunk == b'\n':
                # End of the line
                return message
            message += chunk
        except ConnectionError:
            return None

def display_conversation_header(username):
    """Display conversation header for the given user."""
    print_info(f"\n=== Conversation with {username} ===")

def display_conversation_footer():
    """Display conversation footer."""
    print_info("=== End of conversation ===\n")

def receive_thread_func(sock):
    """Background thread that listens for incoming messages and updates."""
    global current_conversation, should_exit
    
    while not should_exit:
        try:
            data = recv_line_client(sock)
            if data is None:
                print_warning("\nServer disconnected.")
                should_exit = True
                break
            
            response = data.decode().strip()
            if not response:
                continue
            
            # Handle incoming messages from other users
            if response.startswith("[from "):
                # Extract sender from "[from username]: message"
                parts = response.split("]:", 1)
                if len(parts) == 2:
                    sender = parts[0].replace("[from ", "").strip()
                    message_content = parts[1].strip()
                    
                    with active_conversation_lock:
                        # Only display if this is from the current conversation
                        if current_conversation == sender:
                            print_received(f"\n[from {sender}]: {message_content}")
                        else:
                            # Message from someone else - just note it
                            print_warning(f"\n[New message from {sender}] (type /open {sender} to view)")
                continue
            
            # Handle multi-line responses (like /open, /help, /contacts, etc.)
            if "|||" in response:
                lines = response.split("|||")
                print()  # New line for readability
                for line in lines:
                    if line.strip():
                        print_info(line)
                print()  # Newline after multi-line response for spacing
                continue
            
            # Handle conversation displays
            if response.startswith("==="):
                print_info(response)
                continue
            
            # Handle errors
            if "ERROR:" in response:
                print_error(response)
                continue
            
            # Handle single-line info messages
            if any(keyword in response for keyword in ["Connected users:", "Your contacts:", "Started new", "Deleted conversation", "Message sent"]):
                print_info(response)
                continue
            
            # Default handling for other messages
            if response:
                print_info(response)
                
        except Exception as e:
            if not should_exit:
                print_error(f"Error in receive thread: {e}")

def main():
    global current_conversation, sock, should_exit
    
    HOST = input(get_prompt("Enter server IP address >> "))
    if HOST == "":
        HOST = "127.0.0.1"
    PORT = 1337
    USERNAME = input(get_prompt("Enter your username >> "))

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        print_success(f"Connected to {HOST}:{PORT} as {USERNAME}")
        
        # Send username to server
        sock.sendall(USERNAME.encode() + b'\n')

        # Login - Wait for server's first response
        response_bytes = recv_line_client(sock)
        if response_bytes is None:
            print_error("Server closed connection during login.")
            return
        
        response_str = response_bytes.decode()
        print_info(response_str)
        
        if "Enter password:" in response_str:
            password = input(get_prompt(">> "))
            sock.sendall(password.encode() + b'\n')
            
            auth_response_bytes = recv_line_client(sock)
            if auth_response_bytes is None:
                print_error("Login failed. Server disconnected.")
                return
                
            auth_response_str = auth_response_bytes.decode()
            print_success(auth_response_str) if "success" in auth_response_str.lower() else print_info(auth_response_str)
            
            if "ERROR:" in auth_response_str:
                print_error("Authentication failed.")
                return

        elif "registered" in response_str:
            pass
        elif "ERROR:" in response_str:
            return
        else:
            print(f"Unknown server response: {response_str}")
            return

        # Start background receive thread
        receiver = threading.Thread(target=receive_thread_func, args=(sock,), daemon=True)
        receiver.start()

        # Main input loop
        print_info("Commands: /list, /contacts, /open <user>, /delete <user>, /help")
        print_info("To message someone: /msg <username> or type message after /open")
        
        while not should_exit:
            try:
                message = input(get_prompt(">> "))
                if not message:
                    continue
                
                # Handle opening a conversation
                if message.startswith("/open "):
                    username = message.split(" ", 1)[1].strip()
                    with active_conversation_lock:
                        current_conversation = username
                    
                    sock.sendall(message.encode() + b'\n')
                    continue
                
                # Handle /msg command
                if message.startswith("/msg "):
                    parts = message.split(" ", 2)
                    if len(parts) < 3:
                        print_error("Usage: /msg <username> <message>")
                        continue
                    
                    recipient = parts[1]
                    msg_content = parts[2]
                    formatted_msg = f"{recipient}: {msg_content}"
                    
                    with active_conversation_lock:
                        current_conversation = recipient
                    
                    sock.sendall(formatted_msg.encode() + b'\n')
                    continue
                
                # If in a conversation and message is plain text, send it
                with active_conversation_lock:
                    if current_conversation and not message.startswith("/"):
                        formatted_msg = f"{current_conversation}: {message}"
                        sock.sendall(formatted_msg.encode() + b'\n')
                        continue
                
                # Otherwise, send as-is (could be a command)
                sock.sendall(message.encode() + b'\n')
                
            except KeyboardInterrupt:
                print_warning("\nDisconnecting...")
                should_exit = True
                break
            except Exception as e:
                print_error(f"Error: {e}")

    except KeyboardInterrupt:
        print_warning("\nDisconnecting...")
    except ConnectionRefusedError:
        print_error(f"Connection refused. Is the server running on {HOST}:{PORT}?")
    except Exception as e:
        print_error(f"An error occurred: {e}")
    finally:
        should_exit = True
        if sock:
            sock.close()
        print_info("Connection closed.")

if __name__ == "__main__":
    main()