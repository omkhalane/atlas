"""
Decoupled Conversation Service
Handles complete lifecycle operations for conversations without coupling to LLMRuntime internals.
"""
import time
import uuid
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("atlas.llm.conversation")


@dataclass
class ConversationData:
    id: str
    title: str = "New Conversation"
    messages: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    is_archived: bool = False
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class ConversationService:
    def __init__(self):
        self._conversations: Dict[str, ConversationData] = {}

    def create(self, title: str = "New Conversation", conv_id: Optional[str] = None) -> ConversationData:
        cid = conv_id or f"conv-{uuid.uuid4()}"
        conv = ConversationData(id=cid, title=title)
        self._conversations[cid] = conv
        logger.info(f"Created conversation: {cid} ({title})")
        return conv

    def get(self, conv_id: str) -> Optional[ConversationData]:
        return self._conversations.get(conv_id)

    def get_or_create(self, conv_id: str) -> ConversationData:
        conv = self.get(conv_id)
        if not conv:
            conv = self.create(conv_id=conv_id)
        return conv

    def add_message(self, conv_id: str, role: str, content: str, artifacts: List[str] = None):
        conv = self.get_or_create(conv_id)
        msg = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "artifacts": artifacts or [],
            "timestamp": time.time()
        }
        conv.messages.append(msg)
        conv.updated_at = time.time()
        return msg

    def get_recent_messages(self, conv_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        conv = self.get(conv_id)
        if not conv:
            return []
        return conv.messages[-limit:]

    def rename(self, conv_id: str, new_title: str) -> bool:
        conv = self.get(conv_id)
        if conv:
            conv.title = new_title
            conv.updated_at = time.time()
            return True
        return False

    def archive(self, conv_id: str) -> bool:
        conv = self.get(conv_id)
        if conv:
            conv.is_archived = True
            return True
        return False

    def restore(self, conv_id: str) -> bool:
        conv = self.get(conv_id)
        if conv:
            conv.is_archived = False
            return True
        return False

    def delete(self, conv_id: str) -> bool:
        if conv_id in self._conversations:
            del self._conversations[conv_id]
            return True
        return False

    def fork(self, conv_id: str, message_index: Optional[int] = None) -> Optional[ConversationData]:
        parent = self.get(conv_id)
        if not parent:
            return None
        forked_id = f"conv-fork-{uuid.uuid4()}"
        msgs_to_copy = parent.messages[:message_index] if message_index is not None else list(parent.messages)
        forked = ConversationData(
            id=forked_id,
            title=f"Fork of {parent.title}",
            messages=json.loads(json.dumps(msgs_to_copy)),
            artifacts=list(parent.artifacts),
            metadata={"forked_from": conv_id}
        )
        self._conversations[forked_id] = forked
        return forked

    def export_data(self, conv_id: str) -> Optional[Dict[str, Any]]:
        conv = self.get(conv_id)
        if not conv:
            return None
        return {
            "id": conv.id,
            "title": conv.title,
            "messages": conv.messages,
            "summary": conv.summary,
            "metadata": conv.metadata,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at
        }

    def import_data(self, data: Dict[str, Any]) -> ConversationData:
        cid = data.get("id") or f"conv-{uuid.uuid4()}"
        conv = ConversationData(
            id=cid,
            title=data.get("title", "Imported Conversation"),
            messages=data.get("messages", []),
            summary=data.get("summary", ""),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time())
        )
        self._conversations[cid] = conv
        return conv

    def list_conversations(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": c.id,
                "title": c.title,
                "message_count": len(c.messages),
                "is_archived": c.is_archived,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "last_message": c.messages[-1]["content"][:80] if c.messages else ""
            }
            for c in sorted(self._conversations.values(), key=lambda x: x.updated_at, reverse=True)
        ]
