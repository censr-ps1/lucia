import socket
import threading
import os
import sys
from colors import cprint, print_error, print_info, print_success, print_warning, print_received, get_prompt, cstr
from messages import MessageStore

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
# Message store for conversations
message_store = MessageStore()

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

def handle_command(username, command, conn):
    """Handle special commands from the client."""
    try:
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == "/list":
            # List all connected users
            with user_lock:
                user_list = ", ".join(connectedUsers.keys())
            conn.sendall(f"Connected users: {user_list}\n".encode())
        
        elif cmd == "/contacts":
            # List all contacts (users with conversations)
            contacts = message_store.get_user_contacts(username)
            if contacts:
                contact_list = ", ".join(contacts)
                conn.sendall(f"Your contacts: {contact_list}\n".encode())
            else:
                conn.sendall(b"You have no contacts yet.\n")
        
        elif cmd == "/new":
            # Start a new conversation with another user
            if len(parts) < 2:
                conn.sendall(b"ERROR: Usage: /new <username>\n")
                return
            
            recipient = parts[1]
            with user_lock:
                if recipient not in knownUsers:
                    conn.sendall(f"ERROR: User '{recipient}' not found.\n".encode())
                    return
            
            conversation = message_store.get_or_create_conversation(username, recipient)
            conn.sendall(f"Started new conversation with {recipient}.\n".encode())
            print_info(f"New conversation between {username} and {recipient}")
        
        elif cmd == "/open":
            # Open and display a conversation with another user
            if len(parts) < 2:
                conn.sendall(b"ERROR: Usage: /open <username>\n")
                return
            
            recipient = parts[1]
            conversation = message_store.get_conversation(username, recipient)
            
            if not conversation:
                conn.sendall(f"No conversation found with {recipient}.\n".encode())
                return
            
            # Build conversation display as a single message with embedded newlines
            lines = [f"=== Conversation with {recipient} ==="]
            
            messages = conversation.get_messages()
            if not messages:
                lines.append("(No messages yet)")
            else:
                for msg in messages:
                    lines.append(str(msg))
            
            lines.append("=== End of conversation ===")
            
            # Send as a single message (with newlines represented as ||| to avoid protocol issues)
            response = "|||".join(lines)
            conn.sendall(response.encode() + b"\n")
        
        elif cmd == "/delete":
            # Delete a conversation/contact
            if len(parts) < 2:
                conn.sendall(b"ERROR: Usage: /delete <username>\n")
                return
            
            recipient = parts[1]
            if message_store.delete_conversation(username, recipient):
                conn.sendall(f"Deleted conversation with {recipient}.\n".encode())
                print_info(f"Conversation between {username} and {recipient} deleted")
            else:
                conn.sendall(f"No conversation found with {recipient}.\n".encode())
        
        elif cmd == "/help":
            # Display available commands
            # Use ||| as delimiter to safely send multi-line text
            help_lines = [
                "Available commands:",
                "  /list              - List connected users",
                "  /contacts          - List your contacts (users with conversations)",
                "  /new <username>    - Start a new conversation",
                "  /open <username>   - View conversation history with a user",
                "  /delete <username> - Delete a conversation",
                "  /help              - Display this help message",
                "",
                "To send a message: recipient: your message"
            ]
            help_text = "|||".join(help_lines)
            conn.sendall(help_text.encode() + b"\n")
        
        else:
            conn.sendall(f"ERROR: Unknown command '{cmd}'. Type /help for available commands.\n".encode())
    
    except Exception as e:
        print_error(f"Error handling command '{command}' for {username}: {e}")
        try:
            conn.sendall(f"ERROR: {str(e)}\n".encode())
        except:
            pass

def handle_client(conn, addr):
    # Handle a single client connection in its own thread.
    username = None # Define username
    authenticated = False # Flag to track if user was added to lists
    
    try:
        # Read the username
        username_bytes = recv_line(conn)
        if not username_bytes:
            print_warning(f"Connection from {addr} closed before sending username")
            return
        
        username = username_bytes.decode()
        print_info(f"Connected by {addr} as {username}")

        with user_lock:
            if (username in knownUsers):
                
                # Check if user is already connected
                if username in connectedUsers:
                    print_warning(f"{username} is already connected. Disconnecting new session.")
                    conn.sendall(b"ERROR: You are already connected elsewhere.\n")
                    return
                # Send password prompt
                conn.sendall(b"Enter password:\n")
                
                # Read password response
                password_bytes = recv_line(conn)
                if not password_bytes:
                    print_warning(f"{username} ({addr}) disconnected before sending password")
                    return

                password = password_bytes.decode()

                # Check password
                if password != SECRET_PASSWORD:
                    print_error(f"Incorrect password '{password}' from {username} ({addr}). Disconnecting.")
                    return # Close connection by exiting thread
                

                print_success(f"{username} ({addr}) authenticated successfully.")
                # Add to connected users
                connectedUsers[username] = conn 
                authenticated = True # Mark as added to the list
                conn.sendall(b"Authenticated successfully.\n")
                
            else:
                # New user, add them
                print_success(f"New user: {username}. Adding to known users.")
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
                print_info(f"{username} ({addr}) disconnected")
                break
            message = data.decode()
            
            # Handle special commands
            if message.startswith("/"):
                handle_command(username, message, conn)
                continue
            
            # Regular message - parse format: "recipient: message_content"
            if ":" in message:
                parts = message.split(":", 1)
                recipient = parts[0].strip()
                content = parts[1].strip()
                
                # Don't allow sending messages to yourself
                if recipient == username:
                    conn.sendall(b"ERROR: You cannot send messages to yourself.\n")
                    continue
                
                # Check if recipient exists
                with user_lock:
                    if recipient not in knownUsers:
                        conn.sendall(f"ERROR: User '{recipient}' not found.\n".encode())
                        continue
                    recipient_conn = connectedUsers.get(recipient)
                
                # Store message in conversation
                message_store.add_message(username, recipient, content)
                
                # If recipient is connected, forward the message
                if recipient_conn:
                    try:
                        msg_notification = f"[from {username}]: {content}\n"
                        recipient_conn.sendall(msg_notification.encode())
                        print_received(f"Message from {username} to {recipient}: {content!r}")
                    except Exception as e:
                        print_error(f"Failed to deliver message to {recipient}: {e}")
                        conn.sendall(b"ERROR: Failed to deliver message.\n")
                        continue
                
                # Confirm delivery to sender
                conn.sendall(f"Message sent to {recipient}.\n".encode())
            else:
                conn.sendall(b"ERROR: Invalid message format. Use 'recipient: message'\n")
            
    except Exception as e:
        print_error(f"Error with {addr}: {e}")
    finally:
        # Only remove them if they were successfully authenticated and added
        if authenticated:
            with user_lock:
                # Check if they are still in the list before deleting
                if username in connectedUsers:
                    del connectedUsers[username]
                    print_info(f"Removed {username} from connected list.")
        
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
        print_info(f"Server listening on {HOST}:{PORT}")
        
        try:
            while True:
                try:
                    conn, addr = sock.accept()
                    
                    t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                    t.start()
                    
                except socket.timeout:
                    pass 

        except KeyboardInterrupt:
            print_warning("Shutting down server")

if __name__ == '__main__':
    main()