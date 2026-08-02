from pydantic import BaseModel
from typing import List
from runtime.contracts.capability import CapabilityRequest

class Step(BaseModel):
    id: str
    request: CapabilityRequest
    dependencies: List[str] = []

class Plan(BaseModel):
    id: str
    steps: List[Step]
