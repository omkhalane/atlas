from abc import ABC, abstractmethod
from typing import Dict
from atlas.adapters.ports import AdapterPort
from atlas.core.contracts.plugin import PluginManifest

class Plugin(ABC):
    @abstractmethod
    def get_manifest(self) -> PluginManifest:
        pass

    @abstractmethod
    def get_adapters(self) -> Dict[str, AdapterPort]:
        pass
