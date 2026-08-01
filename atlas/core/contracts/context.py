from pydantic import BaseModel
from typing import Dict, Any

class UserIntent(BaseModel):
    text: str
    source: str

class ContextSnapshot(BaseModel):
    intent: UserIntent
    state: Dict[str, Any]
    memory: Dict[str, Any]
