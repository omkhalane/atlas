"""
Provider Router & Intent Routing Engine
"""
import logging
from typing import Dict, Any, Optional, Tuple
from runtime.llm.contracts import ExecutionContext, TaskPriority
from runtime.llm.providers.provider_manager import ProviderManager
from runtime.llm.base_provider import BaseProviderClient
from runtime.llm.capabilities import ProviderCapabilityRegistry

logger = logging.getLogger("atlas.llm.provider_router")


class ProviderRouter:
    def __init__(self, provider_manager: ProviderManager, capability_registry: ProviderCapabilityRegistry):
        self.manager = provider_manager
        self.capabilities = capability_registry

    def select_provider_and_model(
        self,
        ctx: ExecutionContext,
        intent: Optional[str] = None
    ) -> Tuple[BaseProviderClient, str]:
        # Case 1: Specific provider and model requested in ExecutionContext
        if ctx.provider_id:
            client = self.manager.get_client(ctx.provider_id)
            if client:
                model = ctx.model or client.profile.default_model
                return client, model

        # Case 2: Intent-based routing logic
        # Code / Reasoning -> Claude / High Reasoning Model
        # Research / Large context -> Gemini Pro
        # Cheap / Fast -> Flash / Mini / Local Ollama
        default_client = self.manager.get_client()
        if not default_client:
            raise RuntimeError("No provider client available in ProviderManager.")

        model = ctx.model or default_client.profile.default_model

        if intent:
            intent_lower = intent.lower()
            if any(k in intent_lower for k in ["code", "refactor", "bug", "review"]):
                model = "anthropic/claude-sonnet-4-5" if default_client.profile.provider_type == "openai" else default_client.profile.default_model
            elif any(k in intent_lower for k in ["research", "document", "summarize"]):
                model = "google/gemini-2.5-pro" if default_client.profile.provider_type == "openai" else default_client.profile.default_model

        return default_client, model
