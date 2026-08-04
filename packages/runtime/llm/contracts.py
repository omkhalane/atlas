"""
Unified LLM Runtime Contracts & Data Models
"""
import time
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class TaskPriority(Enum):
    CRITICAL_CHAT = 100
    PLANNER = 80
    REFLECTION = 50
    CONVERSATION_SUMMARY = 20
    EMBEDDINGS = 10


class LifecycleState(Enum):
    CREATED = "created"
    QUEUED = "queued"
    LOADING_CONTEXT = "loading_context"
    PROMPT_READY = "prompt_ready"
    EXECUTING = "executing"
    STREAMING = "streaming"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    prompt_cache_hit_tokens: int = 0
    estimated_cost_usd: float = 0.0


@dataclass
class LLMMessage:
    role: str       # "system" | "user" | "assistant" | "tool"
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    cache_control: Optional[Dict[str, str]] = None


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]      # JSON Schema


@dataclass
class ToolCallRequest:
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolCallResult:
    tool_call_id: str
    name: str
    result: Any
    error: Optional[str] = None


@dataclass
class LLMStreamChunk:
    delta_text: str = ""
    delta_reasoning: str = ""
    tool_calls: Optional[List[ToolCallRequest]] = None
    finish_reason: Optional[str] = None
    usage: Optional[TokenUsage] = None


@dataclass
class LLMResponse:
    content: str
    reasoning: Optional[str] = None
    tool_calls: List[ToolCallRequest] = field(default_factory=list)
    finish_reason: str = "stop"
    usage: TokenUsage = field(default_factory=TokenUsage)
    model: str = ""
    provider_id: str = ""


@dataclass
class ProviderProfile:
    id: str
    name: str
    provider_type: str              # "openai" | "anthropic" | "gemini" | "openrouter" | "ollama" | "lmstudio" | "vllm" | "groq" | "custom"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    organization: Optional[str] = None
    default_model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    context_length: int = 128000
    timeout_seconds: int = 60
    max_retries: int = 3
    enable_streaming: bool = True
    enable_prompt_cache: bool = True
    enable_tool_calling: bool = True
    headers: Dict[str, str] = field(default_factory=dict)
    custom_params: Dict[str, Any] = field(default_factory=dict)
    is_default: bool = False
    is_enabled: bool = True


@dataclass
class ExecutionContext:
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = "default"
    task_id: str = ""
    task_type: str = "chat"          # "chat" | "planner" | "summary" | "reflection" | "embeddings"
    priority: TaskPriority = TaskPriority.CRITICAL_CHAT
    provider_id: Optional[str] = None
    model: Optional[str] = None
    workspace_path: Optional[str] = None
    user_id: str = "default_user"
    state: LifecycleState = LifecycleState.CREATED
    cancellation_requested: bool = False
    stream_requested: bool = True
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
