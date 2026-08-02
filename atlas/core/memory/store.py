import sqlite3
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

def _now_utc():
    return datetime.now(timezone.utc)

class Fact:
    def __init__(self, id: str, content: str, provenance: str, expires_at: Optional[datetime] = None, metadata: Dict[str, Any] = None):
        self.id = id
        self.content = content
        self.provenance = provenance
        self.created_at = _now_utc()
        self.expires_at = expires_at
        self.metadata = metadata or {}

class MemoryStore:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        self._load_static_knowledge()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    provenance TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    metadata TEXT
                )
            """)

    def _load_static_knowledge(self):
        import os
        knowledge_file = os.path.join(os.path.dirname(__file__), "linux_commands.json")
        if os.path.exists(knowledge_file):
            try:
                with open(knowledge_file, "r", encoding="utf-8") as f:
                    commands = json.load(f)
                for cmd in commands:
                    fact = Fact(
                        id=f"linux-cmd-{cmd['command']}",
                        content=f"{cmd['command']}: {cmd['description']}",
                        provenance=cmd['source'],
                        expires_at=None,
                        metadata={"type": "linux_command", "command": cmd['command']}
                    )
                    self.store(fact)
            except Exception as e:
                import logging
                logging.getLogger("atlas.memory").error(f"Failed to load static knowledge: {e}")

    def store(self, fact: Fact):
        expires_at_str = fact.expires_at.isoformat() if fact.expires_at else None
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO facts (id, content, provenance, created_at, expires_at, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                (fact.id, fact.content, fact.provenance, fact.created_at.isoformat(), expires_at_str, json.dumps(fact.metadata))
            )

    def search(self, query: str = "") -> List[Fact]:
        cursor = self.conn.cursor()
        now = _now_utc().isoformat()
        
        sql = "SELECT id, content, provenance, created_at, expires_at, metadata FROM facts WHERE (expires_at IS NULL OR expires_at > ?) AND content LIKE ?"
        cursor.execute(sql, (now, f"%{query}%"))
        
        facts = []
        for row in cursor.fetchall():
            expires_at = datetime.fromisoformat(row[4]) if row[4] else None
            fact = Fact(
                id=row[0], 
                content=row[1], 
                provenance=row[2], 
                expires_at=expires_at, 
                metadata=json.loads(row[5])
            )
            fact.created_at = datetime.fromisoformat(row[3])
            facts.append(fact)
        return facts

    def delete_expired(self):
        now = _now_utc().isoformat()
        with self.conn:
            self.conn.execute("DELETE FROM facts WHERE expires_at IS NOT NULL AND expires_at <= ?", (now,))
