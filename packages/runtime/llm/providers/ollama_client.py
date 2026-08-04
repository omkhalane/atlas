"""
Native Ollama Provider Adapter
Communicates with local Ollama daemon (e.g. http://localhost:11434).
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

logger = logging.getLogger("atlas.llm.providers.ollama")


class OllamaProviderClient(BaseProviderClient):
    def __init__(self, profile: ProviderProfile):
        super().__init__(profile)
        self.base_url = (profile.base_url or "http://localhost:11434").rstrip("/")

    async def initialize(self) -> bool:
        health_res = await self.health()
        return health_res.get("status") == "ok"

    async def chat(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[ToolDefinition]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        target_model = model or self.profile.default_model or "qwen2.5-coder:7b"
        endpoint = f"{self.base_url}/api/chat"

        formatted_msgs = [{"role": m.role, "content": m.content} for m in messages]
        payload = {
            "model": target_model,
            "messages": formatted_msgs,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else self.profile.temperature,
            }
        }

        def _make_request():
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=self.profile.timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))

        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, _make_request)
            msg = data.get("message", {})
            content = msg.get("content", "")
            
            prompt_tokens = data.get("prompt_eval_count", 0)
            eval_tokens = data.get("eval_count", 0)
            usage = TokenUsage(prompt_tokens=prompt_tokens, completion_tokens=eval_tokens, total_tokens=prompt_tokens + eval_tokens)

            return LLMResponse(
                content=content,
                finish_reason="stop" if data.get("done") else "length",
                usage=usage,
                model=target_model,
                provider_id=self.profile.id
            )
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
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
        endpoint = f"{self.base_url}/api/embeddings"
        payload = {"model": model or "nomic-embed-text", "prompt": text}
        def _req():
            r = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(r, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _req)
        return data.get("embedding", [])

    async def health(self) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/api/tags"
        def _ping():
            r = urllib.request.Request(endpoint, method="GET")
            with urllib.request.urlopen(r, timeout=3) as resp:
                return resp.status
        try:
            loop = asyncio.get_event_loop()
            st = await loop.run_in_executor(None, _ping)
            return {"status": "ok" if st == 200 else "error"}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}
