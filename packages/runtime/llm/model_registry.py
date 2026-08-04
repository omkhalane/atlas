"""
Model Registry — Catalog & Specs Caching
"""
import time
import logging
from typing import Dict, List, Any, Optional
from runtime.llm.capabilities import ProviderCapabilityRegistry, ModelCapability

logger = logging.getLogger("atlas.llm.model_registry")


class ModelRegistry:
    def __init__(self, capability_registry: ProviderCapabilityRegistry):
        self.capabilities = capability_registry
        self._cached_models: Dict[str, List[Dict[str, Any]]] = {}
        self._last_refresh: float = 0.0
        self.CACHE_TTL = 300  # 5 minutes

    def get_models_for_provider(self, provider_id: str, provider_type: str) -> List[Dict[str, Any]]:
        # Check cache
        if provider_id in self._cached_models and (time.time() - self._last_refresh < self.CACHE_TTL):
            return self._cached_models[provider_id]

        models = self.fetch_available_models(provider_type)
        self._cached_models[provider_id] = models
        return models

    def fetch_available_models(self, provider_type: str) -> List[Dict[str, Any]]:
        known_models = {
            "openai": ["gpt-4o", "gpt-4o-mini", "o1", "o3-mini"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
            "gemini": ["gemini-2.5-pro", "gemini-2.5-flash"],
            "openrouter": [
                "anthropic/claude-sonnet-4-5",
                "google/gemini-2.5-pro",
                "google/gemini-2.5-flash",
                "openai/gpt-4o",
                "deepseek/deepseek-r1",
                "meta-llama/llama-3.3-70b-instruct"
            ],
            "ollama": ["qwen2.5-coder:7b", "llama3.2:3b", "deepseek-r1:8b"],
            "lmstudio": ["local-model"],
            "vllm": ["vllm-model"],
            "groq": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
        }
        model_list = known_models.get(provider_type, ["default-model"])
        
        result = []
        for m in model_list:
            cap = self.capabilities.get_capability(provider_type, m)
            result.append({
                "id": m,
                "name": m,
                "context_window": cap.context_window,
                "max_output_tokens": cap.max_output_tokens,
                "supports_streaming": cap.supports_streaming,
                "supports_tools": cap.supports_tools,
                "supports_vision": cap.supports_vision,
                "supports_reasoning": cap.supports_reasoning,
                "supports_prompt_caching": cap.supports_prompt_caching,
                "input_price_per_m": cap.input_price_per_m,
                "output_price_per_m": cap.output_price_per_m,
            })
        return result
