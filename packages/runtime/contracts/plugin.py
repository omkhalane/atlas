from pydantic import BaseModel
from typing import List
from runtime.capabilities.manifest import CapabilityManifest

class PluginManifest(BaseModel):
    id: str
    name: str
    version: str
    description: str
    capabilities: List[CapabilityManifest] = []
    requested_permissions: List[str] = []
