"""
Phase B: Conversation & Session Manager

ConversationManager: Stores messages, artifacts, and tasks per conversation.
SessionManager: Manages multiple concurrent sessions with TTL eviction.
"""
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger("atlas.session")


@dataclass
class Message:
    role: str       # "user" | "assistant" | "system"
    content: str
    timestamp: float = field(default_factory=time.time)
    artifacts: List[str] = field(default_factory=list)


@dataclass
class Conversation:
    id: str
    messages: List[Message] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    active_task_ids: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str, artifacts: List[str] = None):
        msg = Message(role=role, content=content, artifacts=artifacts or [])
        self.messages.append(msg)
        self.updated_at = time.time()
        return msg

    def get_recent_messages(self, limit: int = 20) -> List[Message]:
        """Returns only recent messages to avoid context overflow."""
        return self.messages[-limit:]

    def get_context_window(self, limit: int = 10) -> List[Dict[str, str]]:
        """Returns messages formatted for LLM consumption — no full dump."""
        return [
            {"role": m.role, "content": m.content}
            for m in self.get_recent_messages(limit)
        ]


class ConversationManager:
    def __init__(self):
        self._conversations: Dict[str, Conversation] = {}

    def get_or_create(self, conversation_id: str) -> Conversation:
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = Conversation(id=conversation_id)
            logger.info(f"Created conversation: {conversation_id}")
        return self._conversations[conversation_id]

    def get(self, conversation_id: str) -> Optional[Conversation]:
        return self._conversations.get(conversation_id)

    def add_user_message(self, conversation_id: str, content: str) -> Message:
        conv = self.get_or_create(conversation_id)
        return conv.add_message("user", content)

    def add_assistant_message(self, conversation_id: str, content: str, artifacts: List[str] = None) -> Message:
        conv = self.get_or_create(conversation_id)
        return conv.add_message("assistant", content, artifacts)

    def get_context(self, conversation_id: str, limit: int = 10) -> List[Dict[str, str]]:
        conv = self.get(conversation_id)
        if not conv:
            return []
        return conv.get_context_window(limit)

    def list_conversations(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": c.id,
                "message_count": len(c.messages),
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "last_message": c.messages[-1].content[:80] if c.messages else ""
            }
            for c in sorted(self._conversations.values(), key=lambda x: x.updated_at, reverse=True)
        ]


class SessionManager:
    """
    Manages multiple concurrent Atlas sessions with TTL eviction.
    A session is an active user connection; conversations persist beyond sessions.
    """
    SESSION_TTL_SECONDS = 3600  # 1 hour

    def __init__(self, conversation_manager: ConversationManager):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self.conversations = conversation_manager

    def start_session(self, session_id: str, conversation_id: str) -> Dict[str, Any]:
        session = {
            "session_id": session_id,
            "conversation_id": conversation_id,
            "started_at": time.time(),
            "last_active": time.time(),
            "status": "active"
        }
        self._sessions[session_id] = session
        self.conversations.get_or_create(conversation_id)
        logger.info(f"Session started: {session_id} → conversation {conversation_id}")
        return session

    def touch(self, session_id: str):
        if session_id in self._sessions:
            self._sessions[session_id]["last_active"] = time.time()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    def evict_expired(self):
        now = time.time()
        expired = [
            sid for sid, s in self._sessions.items()
            if now - s["last_active"] > self.SESSION_TTL_SECONDS
        ]
        for sid in expired:
            del self._sessions[sid]
            logger.info(f"Evicted expired session: {sid}")

    def list_sessions(self) -> List[Dict[str, Any]]:
        return list(self._sessions.values())
