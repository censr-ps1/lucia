"""
Message and conversation management for Lucia.
Handles storage and retrieval of conversations between users.
"""

from datetime import datetime
from typing import Dict, List, Optional

class Message:
    """Represents a single message in a conversation."""
    
    def __init__(self, sender: str, content: str, timestamp: Optional[datetime] = None):
        self.sender = sender
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def __repr__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.sender}: {self.content}"


class Conversation:
    """Represents a conversation between two users."""
    
    def __init__(self, participant1: str, participant2: str):
        # Store participants in sorted order for consistency
        self.participants = tuple(sorted([participant1, participant2]))
        self.messages: List[Message] = []
    
    def add_message(self, sender: str, content: str):
        """Add a message to the conversation."""
        if sender not in self.participants:
            raise ValueError(f"{sender} is not a participant in this conversation")
        self.messages.append(Message(sender, content))
    
    def get_messages(self) -> List[Message]:
        """Get all messages in this conversation."""
        return self.messages
    
    def get_other_participant(self, username: str) -> Optional[str]:
        """Get the other participant's username."""
        if username == self.participants[0]:
            return self.participants[1]
        elif username == self.participants[1]:
            return self.participants[0]
        return None
    
    def __repr__(self):
        return f"Conversation({self.participants[0]} <-> {self.participants[1]}, {len(self.messages)} messages)"


class MessageStore:
    """Manages all conversations across the server."""
    
    def __init__(self):
        # Store conversations by key (tuple of sorted usernames)
        self.conversations: Dict[tuple, Conversation] = {}
    
    def get_conversation_key(self, user1: str, user2: str) -> tuple:
        """Generate a consistent key for a conversation between two users."""
        return tuple(sorted([user1, user2]))
    
    def get_or_create_conversation(self, user1: str, user2: str) -> Conversation:
        """Get an existing conversation or create a new one."""
        key = self.get_conversation_key(user1, user2)
        if key not in self.conversations:
            self.conversations[key] = Conversation(user1, user2)
        return self.conversations[key]
    
    def add_message(self, sender: str, recipient: str, content: str):
        """Add a message to a conversation."""
        conversation = self.get_or_create_conversation(sender, recipient)
        conversation.add_message(sender, content)
    
    def get_conversation(self, user1: str, user2: str) -> Optional[Conversation]:
        """Get a conversation between two users if it exists."""
        key = self.get_conversation_key(user1, user2)
        return self.conversations.get(key)
    
    def get_user_contacts(self, username: str) -> List[str]:
        """Get list of users that the specified user has conversations with."""
        contacts = []
        for key in self.conversations.keys():
            if username in key:
                # Get the other participant
                other = key[0] if key[1] == username else key[1]
                contacts.append(other)
        return sorted(contacts)
    
    def delete_conversation(self, user1: str, user2: str) -> bool:
        """Delete a conversation between two users."""
        key = self.get_conversation_key(user1, user2)
        if key in self.conversations:
            del self.conversations[key]
            return True
        return False
