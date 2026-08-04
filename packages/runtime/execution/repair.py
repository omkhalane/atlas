"""
Self-Healing Repair Engine
Analyzes node execution failure traces and executes targeted micro-repairs before global replanning.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("atlas.execution.repair")


class RepairEngine:
    async def attempt_repair(self, node_id: str, capability_id: str, error_msg: str) -> Optional[Dict[str, Any]]:
        logger.info(f"[RepairEngine] Analyzing failure for node {node_id} ({capability_id}): {error_msg}")
        
        # Repair Strategy 1: Browser selector/DOM timeout
        if capability_id == "browser" and "timeout" in error_msg.lower():
            logger.info(f"[RepairEngine] Strategy: Browser DOM timeout — recommending delay & retry selector.")
            return {"strategy": "retry_with_delay", "delay_seconds": 2.0}

        # Repair Strategy 2: Missing directory path
        if capability_id == "filesystem" and "not found" in error_msg.lower():
            logger.info(f"[RepairEngine] Strategy: Missing directory — recommending mkdir parent.")
            return {"strategy": "ensure_parent_directory"}

        return None
