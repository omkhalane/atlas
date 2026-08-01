from pydantic import BaseModel
from typing import List
from atlas.core.contracts import Step

class Workflow(BaseModel):
    id: str
    name: str
    description: str
    steps: List[Step]
