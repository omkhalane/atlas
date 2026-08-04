"""
Semantic Memory — Vector Embeddings & Similarity Search
"""
import logging
from typing import Dict, List, Any

logger = logging.getLogger("atlas.memory.semantic")


class SemanticMemory:
    def __init__(self):
        self._entries: List[Dict[str, Any]] = []

    def store(self, text: str, embedding: List[float] = None, metadata: Dict[str, Any] = None):
        self._entries.append({
            "text": text,
            "embedding": embedding or [],
            "metadata": metadata or {}
        })

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        q_lower = query.lower()
        results = [e for e in self._entries if q_lower in e["text"].lower()]
        return results[:top_k]
