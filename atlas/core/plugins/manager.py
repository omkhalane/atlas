import importlib.util
import os
import sys
from typing import Dict
from atlas.core.capabilities.engine import CapabilityEngine
from atlas.core.plugins.base import Plugin

class PluginManager:
    def __init__(self, capability_engine: CapabilityEngine):
        self.capability_engine = capability_engine
        self.plugins: Dict[str, Plugin] = {}

    def load_plugin_from_file(self, file_path: str, module_name: str) -> bool:
        if not os.path.exists(file_path):
            return False

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            return False

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        plugin_class = None
        for item_name in dir(module):
            item = getattr(module, item_name)
            if isinstance(item, type) and issubclass(item, Plugin) and item is not Plugin:
                plugin_class = item
                break

        if not plugin_class:
            return False

        plugin_instance = plugin_class()
        manifest = plugin_instance.get_manifest()
        adapters = plugin_instance.get_adapters()

        for cap_manifest in manifest.capabilities:
            if cap_manifest.id in adapters:
                self.capability_engine.register(cap_manifest, adapters[cap_manifest.id])

        self.plugins[manifest.id] = plugin_instance
        return True
