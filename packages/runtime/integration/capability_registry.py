from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from .manifest_schema import CapabilitySchema

class RegisteredCapability(BaseModel):
    capability_id: str
    provider_id: str
    source_type: str  # "native", "plugin", "mcp"
    permissions: List[str]
    status: str  # "available", "disabled", "error"
    schema_def: Optional[Dict[str, Any]] = None

class CapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, RegisteredCapability] = {}
        self._providers: Dict[str, List[str]] = {} # provider_id -> list of capability_ids

    def register(self, capability: RegisteredCapability):
        self._capabilities[capability.capability_id] = capability
        if capability.provider_id not in self._providers:
            self._providers[capability.provider_id] = []
        if capability.capability_id not in self._providers[capability.provider_id]:
            self._providers[capability.provider_id].append(capability.capability_id)

    def unregister_provider(self, provider_id: str):
        if provider_id in self._providers:
            for cap_id in self._providers[provider_id]:
                if cap_id in self._capabilities:
                    del self._capabilities[cap_id]
            del self._providers[provider_id]

    def get_capability(self, capability_id: str) -> Optional[RegisteredCapability]:
        return self._capabilities.get(capability_id)

    def get_all(self) -> List[RegisteredCapability]:
        return list(self._capabilities.values())

    def get_by_provider(self, provider_id: str) -> List[RegisteredCapability]:
        if provider_id not in self._providers:
            return []
        return [self._capabilities[c] for c in self._providers[provider_id] if c in self._capabilities]

# Global instance for the runtime
registry = CapabilityRegistry()
