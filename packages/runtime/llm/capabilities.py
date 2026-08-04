"""
Provider Capability Registry & Pricing System
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class ModelCapability:
    provider: str
    model: str
    version: str = "1.0"
    context_window: int = 128000
    max_output_tokens: int = 4096
    input_price_per_m: float = 0.0      # USD per 1M input tokens
    output_price_per_m: float = 0.0     # USD per 1M output tokens
    supports_streaming: bool = True
    supports_tools: bool = True
    supports_vision: bool = False
    supports_prompt_caching: bool = False
    supports_reasoning: bool = False
    supports_json_mode: bool = True
    supports_structured_output: bool = False
    supports_computer_use: bool = False
    supports_mcp: bool = True
    supports_audio: bool = False


class ProviderCapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, Dict[str, ModelCapability]] = {}
        self._load_defaults()

    def _load_defaults(self):
        # OpenAI Models
        self.register_capability(ModelCapability(
            provider="openai", model="gpt-4o", context_window=128000, max_output_tokens=16384,
            input_price_per_m=2.50, output_price_per_m=10.00,
            supports_vision=True, supports_prompt_caching=True, supports_structured_output=True
        ))
        self.register_capability(ModelCapability(
            provider="openai", model="gpt-4o-mini", context_window=128000, max_output_tokens=16384,
            input_price_per_m=0.15, output_price_per_m=0.60,
            supports_vision=True, supports_prompt_caching=True, supports_structured_output=True
        ))
        self.register_capability(ModelCapability(
            provider="openai", model="o1", context_window=200000, max_output_tokens=100000,
            input_price_per_m=15.00, output_price_per_m=60.00,
            supports_reasoning=True, supports_vision=True, supports_prompt_caching=True
        ))

        # Anthropic Models
        self.register_capability(ModelCapability(
            provider="anthropic", model="claude-3-5-sonnet-20241022", context_window=200000, max_output_tokens=8192,
            input_price_per_m=3.00, output_price_per_m=15.00,
            supports_vision=True, supports_prompt_caching=True, supports_computer_use=True
        ))
        self.register_capability(ModelCapability(
            provider="anthropic", model="claude-3-5-haiku-20241022", context_window=200000, max_output_tokens=8192,
            input_price_per_m=0.80, output_price_per_m=4.00,
            supports_vision=False, supports_prompt_caching=True
        ))

        # Gemini Models
        self.register_capability(ModelCapability(
            provider="google", model="gemini-2.5-pro", context_window=2000000, max_output_tokens=8192,
            input_price_per_m=1.25, output_price_per_m=5.00,
            supports_vision=True, supports_prompt_caching=True, supports_audio=True
        ))
        self.register_capability(ModelCapability(
            provider="google", model="gemini-2.5-flash", context_window=1000000, max_output_tokens=8192,
            input_price_per_m=0.075, output_price_per_m=0.30,
            supports_vision=True, supports_prompt_caching=True, supports_audio=True
        ))

        # Ollama / Local Models (Defaults)
        self.register_capability(ModelCapability(
            provider="ollama", model="qwen2.5-coder:7b", context_window=32768, max_output_tokens=4096,
            input_price_per_m=0.0, output_price_per_m=0.0,
            supports_vision=False, supports_prompt_caching=False
        ))
        self.register_capability(ModelCapability(
            provider="ollama", model="llama3.2:3b", context_window=131072, max_output_tokens=4096,
            input_price_per_m=0.0, output_price_per_m=0.0,
            supports_vision=False, supports_prompt_caching=False
        ))
        self.register_capability(ModelCapability(
            provider="ollama", model="deepseek-r1:8b", context_window=32768, max_output_tokens=4096,
            input_price_per_m=0.0, output_price_per_m=0.0,
            supports_reasoning=True, supports_prompt_caching=False
        ))

    def register_capability(self, cap: ModelCapability):
        if cap.provider not in self._capabilities:
            self._capabilities[cap.provider] = {}
        self._capabilities[cap.provider][cap.model] = cap

    def get_capability(self, provider: str, model: str) -> ModelCapability:
        provider_caps = self._capabilities.get(provider, {})
        if model in provider_caps:
            return provider_caps[model]
        # Return fallback default capability
        return ModelCapability(provider=provider, model=model)

    def supports(self, provider: str, model: str, feature: str) -> bool:
        cap = self.get_capability(provider, model)
        attr = f"supports_{feature}"
        return getattr(cap, attr, False)

    def calculate_cost(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        cap = self.get_capability(provider, model)
        cost = (prompt_tokens / 1_000_000.0) * cap.input_price_per_m + (completion_tokens / 1_000_000.0) * cap.output_price_per_m
        return round(cost, 6)
