from pydantic import BaseModel
from typing import Optional

class PermissionRequest(BaseModel):
    capability_id: str
    action: str
    parameters: dict
    reason: Optional[str] = None

class PolicyDecision(BaseModel):
    allowed: bool
    requires_human: bool = False
    explanation: Optional[str] = None
