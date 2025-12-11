"""Conversation memory and multi-turn query support for RAG."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class MessageRole(str, Enum):
    """Message role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ConversationMessage:
    """A single message in a conversation."""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    citations: List[str] = field(default_factory=list)


@dataclass
class ConversationContext:
    """Context for a conversation including history and state."""
    conversation_id: str
    messages: List[ConversationMessage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_message(
        self,
        role: MessageRole,
        content: str,
        citations: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a message to the conversation."""
        msg = ConversationMessage(
            role=role,
            content=content,
            citations=citations or [],
            metadata=metadata or {}
        )
        self.messages.append(msg)
        self.updated_at = datetime.utcnow()

    def get_recent_context(self, n_messages: int = 5) -> str:
        """Get recent conversation history as formatted text.

        Args:
            n_messages: Number of recent messages to include

        Returns:
            Formatted conversation history
        """
        recent = self.messages[-n_messages:]
        context_parts = []

        for msg in recent:
            role_label = msg.role.value.title()
            context_parts.append(f"{role_label}: {msg.content}")

        return "\n".join(context_parts)

    def get_all_citations(self) -> List[str]:
        """Get all citations used in the conversation."""
        all_citations = []
        for msg in self.messages:
            all_citations.extend(msg.citations)
        return list(set(all_citations))  # Deduplicate


class ConversationMemory:
    """Manages multiple conversation contexts."""

    def __init__(self, max_conversations: int = 100):
        """Initialize conversation memory.

        Args:
            max_conversations: Maximum number of conversations to keep
        """
        self.conversations: Dict[str, ConversationContext] = {}
        self.max_conversations = max_conversations

    def create_conversation(self, conversation_id: str) -> ConversationContext:
        """Create a new conversation context.

        Args:
            conversation_id: Unique identifier for the conversation

        Returns:
            New ConversationContext
        """
        if len(self.conversations) >= self.max_conversations:
            # Remove oldest conversation
            oldest_id = min(
                self.conversations.keys(),
                key=lambda k: self.conversations[k].updated_at
            )
            del self.conversations[oldest_id]

        context = ConversationContext(conversation_id=conversation_id)
        self.conversations[conversation_id] = context
        return context

    def get_conversation(
        self,
        conversation_id: str,
        create_if_missing: bool = True
    ) -> Optional[ConversationContext]:
        """Get a conversation context by ID.

        Args:
            conversation_id: Conversation identifier
            create_if_missing: Create new context if not found

        Returns:
            ConversationContext or None
        """
        if conversation_id not in self.conversations and create_if_missing:
            return self.create_conversation(conversation_id)

        return self.conversations.get(conversation_id)

    def delete_conversation(self, conversation_id: str):
        """Delete a conversation context."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]

    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all active conversations.

        Returns:
            List of conversation summaries
        """
        summaries = []
        for conv_id, context in self.conversations.items():
            summaries.append({
                "conversation_id": conv_id,
                "message_count": len(context.messages),
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat(),
                "last_message": context.messages[-1].content[:100] if context.messages else None
            })

        return sorted(summaries, key=lambda x: x["updated_at"], reverse=True)


class QueryRewriter:
    """Rewrites queries based on conversation context."""

    def rewrite_with_context(
        self,
        current_query: str,
        conversation_context: ConversationContext,
        n_context_messages: int = 3
    ) -> str:
        """Rewrite a query considering conversation history.

        This helps resolve pronouns and references to previous context.

        Args:
            current_query: Current user query
            conversation_context: Conversation history
            n_context_messages: Number of previous messages to consider

        Returns:
            Rewritten query with context
        """
        if len(conversation_context.messages) == 0:
            return current_query

        # Get recent context
        recent_context = conversation_context.get_recent_context(n_context_messages)

        # Check if query has pronouns or references that need resolution
        pronouns = ["it", "that", "this", "they", "them", "there", "those"]
        has_pronoun = any(pronoun in current_query.lower().split() for pronoun in pronouns)

        if not has_pronoun:
            return current_query

        # Build contextualized query
        contextualized = f"""Previous conversation:
{recent_context}

Current question: {current_query}

(Interpret the current question in the context of the conversation above)"""

        return contextualized

    def extract_geography_from_context(
        self,
        conversation_context: ConversationContext
    ) -> Optional[str]:
        """Extract geography references from conversation history.

        Returns:
            Most recently mentioned geography or None
        """
        # Simple pattern matching for state names
        state_names = [
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
            "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
            "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
            "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
            "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
            "New Hampshire", "New Jersey", "New Mexico", "New York",
            "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
            "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
            "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
            "West Virginia", "Wisconsin", "Wyoming"
        ]

        # Search recent messages for state names
        for msg in reversed(conversation_context.messages):
            for state in state_names:
                if state.lower() in msg.content.lower():
                    return state

        return None
