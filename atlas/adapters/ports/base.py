from abc import ABC, abstractmethod
from atlas.core.contracts import CapabilityRequest, CapabilityResult

class AdapterPort(ABC):
    @abstractmethod
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        pass
