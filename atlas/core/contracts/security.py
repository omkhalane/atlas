from pydantic import BaseModel
from typing import Optional

class PermissionRequest(BaseModel):
    capability_id: str
    scope: str
    reason: str

class PolicyDecision(BaseModel):
    allowed: bool
    explanation: Optional[str] = None
