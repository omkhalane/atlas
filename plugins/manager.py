import importlib.util
import os
import sys
from typing import Dict, TYPE_CHECKING
from plugins.base import Plugin

if TYPE_CHECKING:
    from runtime.capabilities.registry import CapabilityRegistry

class PluginManager:
    def __init__(self, capability_registry: 'CapabilityRegistry'):
        self.capability_registry = capability_registry
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
                self.capability_registry.register(cap_manifest.id, adapters[cap_manifest.id])

        self.plugins[manifest.id] = plugin_instance
        return True

    def auto_load_plugins(self, plugins_dir: str = "/code/ATLAS/.atlas/plugins"):
        """Scans the plugins directory and loads any .py files as plugins."""
        import glob
        if not os.path.exists(plugins_dir):
            return
            
        for file_path in glob.glob(os.path.join(plugins_dir, "*.py")):
            module_name = f"atlas.plugin_{os.path.basename(file_path)[:-3]}"
            try:
                self.load_plugin_from_file(file_path, module_name)
            except Exception:
                pass
