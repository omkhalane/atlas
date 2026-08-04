"""
OpenAI & OpenAI-Compatible Provider Adapter
Translates standard LLM requests into OpenAI Chat Completions REST API protocol.
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

logger = logging.getLogger("atlas.llm.providers.openai")


class OpenAIProviderClient(BaseProviderClient):
    def __init__(self, profile: ProviderProfile):
        super().__init__(profile)
        self.base_url = (profile.base_url or "https://api.openai.com/v1").rstrip("/")
        self.api_key = profile.api_key or ""

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Atlas-LLM-Runtime/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.profile.organization:
            headers["OpenAI-Organization"] = self.profile.organization
        for k, v in self.profile.headers.items():
            headers[k] = v
        return headers

    def _format_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        formatted = []
        for m in messages:
            msg_dict: Dict[str, Any] = {"role": m.role, "content": m.content}
            if m.name:
                msg_dict["name"] = m.name
            if m.tool_call_id:
                msg_dict["tool_call_id"] = m.tool_call_id
            if m.tool_calls:
                msg_dict["tool_calls"] = m.tool_calls
            formatted.append(msg_dict)
        return formatted

    def _format_tools(self, tools: Optional[List[ToolDefinition]]) -> Optional[List[Dict[str, Any]]]:
        if not tools:
            return None
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters
                }
            }
            for t in tools
        ]

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
        target_model = model or self.profile.default_model
        endpoint = f"{self.base_url}/chat/completions"

        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": self._format_messages(messages),
            "temperature": temperature if temperature is not None else self.profile.temperature,
            "max_tokens": max_tokens or self.profile.max_tokens,
            "stream": False,
        }

        formatted_tools = self._format_tools(tools)
        if formatted_tools and self.profile.enable_tool_calling:
            payload["tools"] = formatted_tools

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
            choice = data["choices"][0]
            msg = choice.get("message", {})
            content = msg.get("content") or ""
            reasoning = msg.get("reasoning_content") or msg.get("reasoning")
            
            tool_calls_req = []
            if "tool_calls" in msg:
                for tc in msg["tool_calls"]:
                    func = tc.get("function", {})
                    args = json.loads(func.get("arguments", "{}")) if isinstance(func.get("arguments"), str) else func.get("arguments", {})
                    tool_calls_req.append(ToolCallRequest(
                        id=tc.get("id", ""),
                        name=func.get("name", ""),
                        arguments=args
                    ))

            usage_raw = data.get("usage", {})
            usage = TokenUsage(
                prompt_tokens=usage_raw.get("prompt_tokens", 0),
                completion_tokens=usage_raw.get("completion_tokens", 0),
                total_tokens=usage_raw.get("total_tokens", 0),
                prompt_cache_hit_tokens=usage_raw.get("prompt_tokens_details", {}).get("cached_tokens", 0)
            )

            return LLMResponse(
                content=content,
                reasoning=reasoning,
                tool_calls=tool_calls_req,
                finish_reason=choice.get("finish_reason", "stop"),
                usage=usage,
                model=target_model,
                provider_id=self.profile.id
            )
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8") if e.fp else str(e)
            logger.error(f"OpenAI HTTP error [{e.code}]: {err_body}")
            raise RuntimeError(f"OpenAI Provider Error ({e.code}): {err_body}") from e
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
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
        # Non-blocking streaming generator yielding chunks
        res = await self.chat(messages, tools, model, temperature, max_tokens, extra_params)
        yield LLMStreamChunk(
            delta_text=res.content,
            delta_reasoning=res.reasoning or "",
            tool_calls=res.tool_calls,
            finish_reason=res.finish_reason,
            usage=res.usage
        )

    async def embeddings(self, text: str, model: Optional[str] = None) -> List[float]:
        endpoint = f"{self.base_url}/embeddings"
        payload = {
            "input": text,
            "model": model or "text-embedding-3-small"
        }
        def _make_req():
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers=self._get_headers(),
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, _make_req)
        return data["data"][0]["embedding"]

    async def health(self) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/models"
        def _ping():
            req = urllib.request.Request(endpoint, headers=self._get_headers(), method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status
        try:
            loop = asyncio.get_event_loop()
            status = await loop.run_in_executor(None, _ping)
            return {"status": "ok" if status == 200 else "degraded", "code": status}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}
