"""
Provider Profile & Factory Manager
Manages profile configurations, dynamic provider instantiation, and instant profile switching.
"""
import logging
from typing import Dict, List, Optional
from runtime.llm.contracts import ProviderProfile
from runtime.llm.base_provider import BaseProviderClient
from runtime.llm.providers.openai_client import OpenAIProviderClient
from runtime.llm.providers.anthropic_client import AnthropicProviderClient
from runtime.llm.providers.ollama_client import OllamaProviderClient

logger = logging.getLogger("atlas.llm.provider_manager")


class ProviderManager:
    def __init__(self):
        self._profiles: Dict[str, ProviderProfile] = {}
        self._clients: Dict[str, BaseProviderClient] = {}
        self._default_profile_id: Optional[str] = None
        self._load_default_profiles()

    def _load_default_profiles(self):
        # Default 1: OpenRouter (Cloud Gateway)
        import os
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "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")
        openrouter_prof = ProviderProfile(
            id="openrouter-default",
            name="OpenRouter Cloud",
            provider_type="openai",
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key,
            default_model="anthropic/claude-sonnet-4-5",
            is_default=True
        )
        self.add_profile(openrouter_prof)

        # Default 2: Local Ollama
        ollama_prof = ProviderProfile(
            id="ollama-local",
            name="Local Ollama",
            provider_type="ollama",
            base_url="http://localhost:11434",
            default_model="qwen2.5-coder:7b",
            is_default=False
        )
        self.add_profile(ollama_prof)

        # Default 3: Local LM Studio
        lmstudio_prof = ProviderProfile(
            id="lmstudio-local",
            name="Office LM Studio",
            provider_type="openai",
            base_url="http://127.0.0.1:8000/v1",
            default_model="local-model",
            is_default=False
        )
        self.add_profile(lmstudio_prof)

    def create_client(self, profile: ProviderProfile) -> BaseProviderClient:
        ptype = profile.provider_type.lower()
        if ptype == "anthropic":
            return AnthropicProviderClient(profile)
        elif ptype == "ollama":
            return OllamaProviderClient(profile)
        else:
            # Default to OpenAI-compatible client (OpenAI, Azure, OpenRouter, LMStudio, vLLM, Groq, etc.)
            return OpenAIProviderClient(profile)

    def add_profile(self, profile: ProviderProfile):
        self._profiles[profile.id] = profile
        self._clients[profile.id] = self.create_client(profile)
        if profile.is_default or not self._default_profile_id:
            self.set_default_profile(profile.id)
        logger.info(f"Registered provider profile: {profile.name} ({profile.id})")

    def update_profile(self, profile: ProviderProfile):
        self.add_profile(profile)

    def remove_profile(self, profile_id: str):
        if profile_id in self._profiles:
            del self._profiles[profile_id]
        if profile_id in self._clients:
            del self._clients[profile_id]
        if self._default_profile_id == profile_id:
            remaining = list(self._profiles.keys())
            self._default_profile_id = remaining[0] if remaining else None

    def set_default_profile(self, profile_id: str):
        if profile_id in self._profiles:
            for pid, prof in self._profiles.items():
                prof.is_default = (pid == profile_id)
            self._default_profile_id = profile_id

    def get_profile(self, profile_id: Optional[str] = None) -> Optional[ProviderProfile]:
        target_id = profile_id or self._default_profile_id
        return self._profiles.get(target_id) if target_id else None

    def get_client(self, profile_id: Optional[str] = None) -> Optional[BaseProviderClient]:
        target_id = profile_id or self._default_profile_id
        if target_id and target_id in self._clients:
            return self._clients[target_id]
        profile = self.get_profile(target_id)
        if profile:
            client = self.create_client(profile)
            self._clients[profile.id] = client
            return client
        return None

    def list_profiles(self) -> List[ProviderProfile]:
        return list(self._profiles.values())
