from abc import ABC, abstractmethod
from typing import List
import sqlite3
import json
from datetime import datetime
from atlas.core.contracts import Event

class TransactionLedger(ABC):
    @abstractmethod
    def append(self, event: Event):
        pass
        
    @abstractmethod
    def get_history(self, limit: int = 100) -> List[Event]:
        pass

class SQLiteLedger(TransactionLedger):
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
            """)

    def append(self, event: Event):
        with self.conn:
            self.conn.execute(
                "INSERT INTO events (id, type, timestamp, payload) VALUES (?, ?, ?, ?)",
                (event.id, event.type, event.timestamp.isoformat(), json.dumps(event.payload))
            )

    def get_history(self, limit: int = 100) -> List[Event]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, type, timestamp, payload FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
        
        events = []
        for row in cursor.fetchall():
            events.append(Event(
                id=row[0],
                type=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                payload=json.loads(row[3])
            ))
        return events
