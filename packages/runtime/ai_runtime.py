"""
Top-Level Enterprise AI Platform Runtime (AIRuntime)
Unites Event Store, Job Dispatcher, Execution Workers, Execution Engine, Memory Runtime, OS Resources & LLM Runtime.
"""
import logging
from typing import Dict, Any, Optional

from runtime.events.store import EventStore
from runtime.memory.runtime import MemoryRuntime
from runtime.resources.os_resource_manager import OSResourceManager
from runtime.scheduler.queue import PriorityScheduler
from runtime.scheduler.dispatcher import JobDispatcher
from runtime.execution.engine import ExecutionEngine
from runtime.policy.approval import ResumableApprovalManager
from runtime.llm.runtime import LLMRuntime
from runtime.observability.telemetry import ObservabilityEngine
from runtime.health.health_monitor import ProviderHealthMonitor
from runtime.cache.cache_manager import UnifiedCacheManager
from runtime.recovery.recovery_manager import RecoveryManager
from runtime.plugins.plugin_engine import PluginEngine
from runtime.features.feature_flags import FeatureFlags

logger = logging.getLogger("atlas.ai_runtime")


class AIRuntime:
    def __init__(self, memory_engine=None, capability_registry=None):
        # Persistent Event Store & Sourcing
        self.event_store = EventStore()

        # Decoupled Memory Subsystem
        self.memory = MemoryRuntime()

        # OS-Level Resource & Slot Management
        self.os_resources = OSResourceManager()

        # Job Dispatcher & Isolated Capability Worker Registry
        self.dispatcher = JobDispatcher()

        # Airflow-Style Execution Engine (DAG Walker)
        self.execution_engine = ExecutionEngine(self.dispatcher, self.event_store)

        # Resumable Human Approval Engine
        self.approval = ResumableApprovalManager()

        # Priority Scheduler
        self.scheduler = PriorityScheduler(max_concurrent=10)

        # Dedicated Language Core (LLM Runtime)
        self.llm = LLMRuntime(memory_engine=self.memory, capability_registry_atlas=capability_registry)

        # Observability & Health Monitors
        self.observability = ObservabilityEngine()
        self.health = ProviderHealthMonitor(self.llm.providers)

        # Caching, Recovery, Plugins & Feature Flags
        self.cache = UnifiedCacheManager()
        self.recovery = RecoveryManager()
        self.plugins = PluginEngine()
        self.features = FeatureFlags()

    async def start(self):
        await self.llm.initialize()
        logger.info("AIRuntime Enterprise Platform operational.")

    async def shutdown(self):
        await self.llm.shutdown()
        logger.info("AIRuntime Enterprise Platform shut down.")
