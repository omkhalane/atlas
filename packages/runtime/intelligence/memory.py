"""
Phase F: Upgraded MemoryEngine with Semantic Search via Ollama Embeddings.
Also retains the original SQLite key-value store for procedural rules and facts.
"""
import os
import sqlite3
import json
import logging
import math
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING

logger = logging.getLogger("atlas.memory")

if TYPE_CHECKING:
    from runtime.intelligence.local_llm import LocalLLMManager


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Pure Python cosine similarity — no numpy dependency."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


class MemoryEngine:
    def __init__(self, db_path: str = "/code/ATLAS/.atlas/memory.db", local_llm: Optional['LocalLLMManager'] = None):
        self.db_path = db_path
        self.local_llm = local_llm
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def set_local_llm(self, local_llm: 'LocalLLMManager'):
        """Allows injecting LocalLLM after initialization (since Ollama may not be ready at boot)."""
        self.local_llm = local_llm

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Key-value store for facts and procedural rules
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Semantic vector store
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    # ── Key-Value Store ───────────────────────────────────────────────────────

    def store(self, category: str, key: str, value: str):
        """Stores a fact or procedural rule in long-term key-value memory."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO memory (category, key, value)
                    VALUES (?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value, created_at=CURRENT_TIMESTAMP
                """, (category, key, value))
                conn.commit()
            logger.info(f"Stored [{category}] {key}")
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")

    def get(self, key: str) -> Optional[str]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM memory WHERE key = ?", (key,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get memory {key}: {e}")
            return None

    def get_all_by_category(self, category: str) -> List[Dict[str, str]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM memory WHERE category = ?", (category,))
                return [{"key": row[0], "value": row[1]} for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get memories for category {category}: {e}")
            return []

    def get_context_summary(self) -> str:
        """Returns formatted string of all procedural rules and key facts for the LLM prompt."""
        rules = self.get_all_by_category("procedural")
        facts = self.get_all_by_category("fact")
        lines = []
        if rules:
            lines.append("Procedural Rules (Always Follow):")
            for r in rules:
                lines.append(f"- {r['key']}: {r['value']}")
        if facts:
            lines.append("Learned Facts:")
            for f in facts:
                lines.append(f"- {f['key']}: {f['value']}")
        return "\n".join(lines)

    # ── Semantic Vector Store ────────────────────────────────────────────────

    def store_semantic(self, text: str, metadata: dict = None) -> bool:
        """
        Embeds text using Ollama and stores it in the vector store.
        Used for semantic memory search (Phase F).
        """
        if not self.local_llm or not self.local_llm.ollama_available:
            logger.debug("Semantic store skipped — no local LLM")
            return False

        try:
            embedding = self.local_llm.get_embedding(text)
            if not embedding:
                return False

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO embeddings (text, embedding, metadata) VALUES (?, ?, ?)",
                    (text, json.dumps(embedding), json.dumps(metadata or {}))
                )
                conn.commit()
            logger.info(f"Stored semantic memory: {text[:60]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to store semantic memory: {e}")
            return False

    def search_similar(self, query: str, top_k: int = 5, threshold: float = 0.7) -> List[Dict]:
        """
        Retrieves semantically similar memories using cosine similarity.
        Falls back to empty list if Ollama is unavailable.
        """
        if not self.local_llm or not self.local_llm.ollama_available:
            return []

        try:
            query_embedding = self.local_llm.get_embedding(query)
            if not query_embedding:
                return []

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT text, embedding, metadata FROM embeddings")
                rows = cursor.fetchall()

            results: List[Tuple[float, str, dict]] = []
            for text, emb_json, meta_json in rows:
                emb = json.loads(emb_json)
                sim = _cosine_similarity(query_embedding, emb)
                if sim >= threshold:
                    results.append((sim, text, json.loads(meta_json)))

            results.sort(key=lambda x: x[0], reverse=True)
            return [{"text": r[1], "score": r[0], "metadata": r[2]} for r in results[:top_k]]

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
