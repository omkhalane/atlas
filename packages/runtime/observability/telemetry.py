"""
Observability & Telemetry Engine
"""
import time
import logging
from typing import Dict, List, Any
from dataclasses import dataclass, field

logger = logging.getLogger("atlas.observability")


@dataclass
class TraceRecord:
    request_id: str
    task_type: str
    provider_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    latency_ms: float
    timestamp: float = field(default_factory=time.time)


class ObservabilityEngine:
    def __init__(self):
        self._traces: List[TraceRecord] = []
        self._total_cost_usd: float = 0.0
        self._total_requests: int = 0

    def record_trace(
        self,
        request_id: str,
        task_type: str,
        provider_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        latency_ms: float
    ):
        record = TraceRecord(
            request_id=request_id,
            task_type=task_type,
            provider_id=provider_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost_usd=cost_usd,
            latency_ms=latency_ms
        )
        self._traces.append(record)
        self._total_cost_usd += cost_usd
        self._total_requests += 1

    def get_metrics_summary(self) -> Dict[str, Any]:
        total_tokens = sum(t.total_tokens for t in self._traces)
        avg_latency = (sum(t.latency_ms for t in self._traces) / len(self._traces)) if self._traces else 0.0
        return {
            "total_requests": self._total_requests,
            "total_tokens": total_tokens,
            "total_cost_usd": round(self._total_cost_usd, 6),
            "average_latency_ms": round(avg_latency, 2),
            "trace_count": len(self._traces)
        }
