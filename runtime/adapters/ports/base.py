from abc import ABC, abstractmethod
from runtime.contracts import CapabilityRequest, CapabilityResult

class AdapterPort(ABC):
    @abstractmethod
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        pass
