"""
Provider Health Monitor
Background worker that periodically tests provider endpoints for latency, uptime, and status.
"""
import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("atlas.health_monitor")


class ProviderHealthMonitor:
    def __init__(self, provider_manager=None):
        self.manager = provider_manager
        self._health_status: Dict[str, Dict[str, Any]] = {}
        self._running = False

    async def check_provider_health(self, profile_id: str) -> Dict[str, Any]:
        if not self.manager:
            return {"status": "unknown"}
        client = self.manager.get_client(profile_id)
        if not client:
            return {"status": "not_configured"}
        try:
            status = await client.health()
            self._health_status[profile_id] = status
            return status
        except Exception as e:
            res = {"status": "degraded", "error": str(e)}
            self._health_status[profile_id] = res
            return res

    def get_all_health(self) -> Dict[str, Dict[str, Any]]:
        return self._health_status
