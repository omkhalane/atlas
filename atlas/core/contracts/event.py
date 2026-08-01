from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime, timezone

def _now_utc():
    return datetime.now(timezone.utc)

class Event(BaseModel):
    id: str
    type: str
    timestamp: datetime = Field(default_factory=_now_utc)
    payload: Dict[str, Any]
