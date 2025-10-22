"""Conversation memory for agents"""

from typing import List, Optional

from axm.core.types import Message


class ConversationMemory:
    """Simple conversation memory that stores messages"""

    def __init__(self, max_messages: Optional[int] = None):
        """
        Initialize conversation memory.

        Args:
            max_messages: Maximum number of messages to keep (None for unlimited)
        """
        self.messages: List[Message] = []
        self.max_messages = max_messages

    def add_message(self, message: Message) -> None:
        """Add a message to memory"""
        self.messages.append(message)

        # Enforce max messages limit
        if self.max_messages is not None and len(self.messages) > self.max_messages:
            # Keep system messages if they exist
            system_messages = [msg for msg in self.messages if msg.role == "system"]
            # Keep the last N messages excluding system messages
            other_messages = [msg for msg in self.messages if msg.role != "system"]
            other_messages = other_messages[-(self.max_messages - len(system_messages)) :]

            self.messages = system_messages + other_messages

    def clear(self) -> None:
        """Clear all messages from memory"""
        self.messages.clear()

    def get_last_n(self, n: int) -> List[Message]:
        """Get the last n messages"""
        return self.messages[-n:]

    def filter_by_role(self, role: str) -> List[Message]:
        """Get all messages from a specific role"""
        return [msg for msg in self.messages if msg.role == role]

    def __len__(self) -> int:
        """Get the number of messages"""
        return len(self.messages)

    def __getitem__(self, index: int) -> Message:
        """Get message by index"""
        return self.messages[index]