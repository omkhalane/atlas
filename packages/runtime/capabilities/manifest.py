from pydantic import BaseModel
from typing import List

class CapabilityParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True

class CapabilityManifest(BaseModel):
    id: str
    description: str
    version: str
    parameters: List[CapabilityParameter] = []
    required_permissions: List[str] = []
