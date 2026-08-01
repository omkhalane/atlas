from pydantic import BaseModel
from typing import Dict, Any, Optional

class CapabilityRequest(BaseModel):
    id: str
    parameters: Dict[str, Any]

class CapabilityResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
