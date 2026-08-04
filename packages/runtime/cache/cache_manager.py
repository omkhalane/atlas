"""
Unified Cache Manager
Single abstraction for Prompts, Memories, Models, Capabilities, and Embeddings.
"""
import time
from typing import Dict, Any, Optional


class UnifiedCacheManager:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, namespace: str, key: str) -> Optional[Any]:
        ns = self._cache.get(namespace, {})
        item = ns.get(key)
        if not item:
            return None
        if item["expires_at"] and time.time() > item["expires_at"]:
            del ns[key]
            return None
        return item["value"]

    def set(self, namespace: str, key: str, value: Any, ttl_seconds: Optional[int] = None):
        if namespace not in self._cache:
            self._cache[namespace] = {}
        expires_at = (time.time() + ttl_seconds) if ttl_seconds else None
        self._cache[namespace][key] = {"value": value, "expires_at": expires_at}

    def clear(self, namespace: Optional[str] = None):
        if namespace:
            self._cache.pop(namespace, None)
        else:
            self._cache.clear()
