"""
Abstract Base Provider Client Interface
Providers are pure translation adapters with ZERO business logic.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator, Optional
from runtime.llm.contracts import (
    ProviderProfile, LLMMessage, LLMResponse, LLMStreamChunk, ToolDefinition
)
from runtime.llm.capabilities import ModelCapability


class BaseProviderClient(ABC):
    def __init__(self, profile: ProviderProfile):
        self.profile = profile

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize connection, validate credentials or health."""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[ToolDefinition]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """Synchronous/standard complete chat call."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[ToolDefinition]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        """Streaming chat token generator."""
        pass

    @abstractmethod
    async def embeddings(self, text: str, model: Optional[str] = None) -> List[float]:
        """Generates embedding vector for given text."""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Health ping test."""
        pass
