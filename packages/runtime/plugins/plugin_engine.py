"""
Plugin Engine — Extension Module Exporter & Loader
"""
import logging
from typing import Dict, List, Any

logger = logging.getLogger("atlas.plugins")


class PluginEngine:
    def __init__(self):
        self._plugins: Dict[str, Any] = {}

    def register_plugin(self, plugin_id: str, plugin_instance: Any):
        self._plugins[plugin_id] = plugin_instance
        logger.info(f"Registered plugin extension: {plugin_id}")

    def get_plugin(self, plugin_id: str) -> Any:
        return self._plugins.get(plugin_id)

    def list_plugins(self) -> List[str]:
        return list(self._plugins.keys())
