"""
Anthropic Claude Provider Adapter
Translates standard LLM requests into Anthropic Messages API.
"""
import json
import asyncio
import logging
from typing import List, Dict, Any, AsyncGenerator, Optional
import urllib.request
import urllib.error

from runtime.llm.base_provider import BaseProviderClient
from runtime.llm.contracts import (
    ProviderProfile, LLMMessage, LLMResponse, LLMStreamChunk,
    ToolDefinition, ToolCallRequest, TokenUsage
)

logger = logging.getLogger("atlas.llm.providers.anthropic")


class AnthropicProviderClient(BaseProviderClient):
    def __init__(self, profile: ProviderProfile):
        super().__init__(profile)
        self.base_url = (profile.base_url or "https://api.anthropic.com/v1").rstrip("/")
        self.api_key = profile.api_key or ""

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "User-Agent": "Atlas-LLM-Runtime/1.0"
        }
        if self.profile.enable_prompt_cache:
            headers["anthropic-beta"] = "prompt-caching-2024-07-31"
        for k, v in self.profile.headers.items():
            headers[k] = v
        return headers

    def _format_messages_and_system(self, messages: List[LLMMessage]):
        system_prompt = ""
        anthropic_msgs = []
        for m in messages:
            if m.role == "system":
                system_prompt += m.content + "\n"
            else:
                role = "assistant" if m.role == "assistant" else "user"
                msg_obj: Dict[str, Any] = {"role": role, "content": m.content}
                if m.cache_control and self.profile.enable_prompt_cache:
                    msg_obj["cache_control"] = m.cache_control
                anthropic_msgs.append(msg_obj)

        system_payload = None
        if system_prompt:
            system_payload = [{"type": "text", "text": system_prompt.strip()}]
            if self.profile.enable_prompt_cache:
                system_payload[0]["cache_control"] = {"type": "ephemeral"}

        return anthropic_msgs, system_payload

    async def initialize(self) -> bool:
        health_status = await self.health()
        return health_status.get("status") == "ok"

    async def chat(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[ToolDefinition]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        target_model = model or self.profile.default_model or "claude-3-5-sonnet-20241022"
        endpoint = f"{self.base_url}/messages"

        anthropic_msgs, system_payload = self._format_messages_and_system(messages)
        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": anthropic_msgs,
            "max_tokens": max_tokens or self.profile.max_tokens or 4096,
            "temperature": temperature if temperature is not None else self.profile.temperature,
        }
        if system_payload:
            payload["system"] = system_payload

        if extra_params:
            payload.update(extra_params)

        def _make_request():
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers=self._get_headers(),
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=self.profile.timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))

        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, _make_request)
            content = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    content += block.get("text", "")

            usage_raw = data.get("usage", {})
            usage = TokenUsage(
                prompt_tokens=usage_raw.get("input_tokens", 0),
                completion_tokens=usage_raw.get("output_tokens", 0),
                total_tokens=usage_raw.get("input_tokens", 0) + usage_raw.get("output_tokens", 0),
                prompt_cache_hit_tokens=usage_raw.get("cache_read_input_tokens", 0)
            )

            return LLMResponse(
                content=content,
                finish_reason=data.get("stop_reason", "end_turn"),
                usage=usage,
                model=target_model,
                provider_id=self.profile.id
            )
        except Exception as e:
            logger.error(f"Anthropic request failed: {e}")
            raise

    async def stream(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[ToolDefinition]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        res = await self.chat(messages, tools, model, temperature, max_tokens, extra_params)
        yield LLMStreamChunk(delta_text=res.content, finish_reason=res.finish_reason, usage=res.usage)

    async def embeddings(self, text: str, model: Optional[str] = None) -> List[float]:
        # Anthropic doesn't have an embeddings API — return zero vector or raise
        raise NotImplementedError("Anthropic does not offer an embeddings endpoint.")

    async def health(self) -> Dict[str, Any]:
        return {"status": "ok" if self.api_key else "missing_key"}
