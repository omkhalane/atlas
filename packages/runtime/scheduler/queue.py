"""
Priority Scheduler & Task Lifecycle State Machine
Prioritizes Interactive Chat > Planner > Reflection > Summary > Embeddings.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from heapq import heappush, heappop
from enum import Enum
from runtime.llm.contracts import ExecutionContext, TaskPriority, LifecycleState

logger = logging.getLogger("atlas.scheduler")


class TaskLifecycleState(Enum):
    CREATED = "created"
    QUEUED = "queued"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING = "waiting"         # Waiting for human approval or async resource
    RETRYING = "retrying"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class PriorityScheduler:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._queue: List[tuple[int, float, ExecutionContext, Any]] = []
        self._active_count = 0
        self._lock = asyncio.Lock()

    async def enqueue(self, ctx: ExecutionContext, task_func, *args, **kwargs):
        ctx.state = LifecycleState.QUEUED
        priority_score = -ctx.priority.value
        item = (priority_score, ctx.created_at, ctx, (task_func, args, kwargs))
        
        async with self._lock:
            heappush(self._queue, item)
            logger.info(f"Enqueued task {ctx.task_id or ctx.request_id} (priority={ctx.priority.name})")

        return await self._process_next()

    async def _process_next(self):
        async with self._lock:
            if self._active_count >= self.max_concurrent or not self._queue:
                return None

            priority_score, created_at, ctx, (task_func, args, kwargs) = heappop(self._queue)
            self._active_count += 1

        ctx.state = LifecycleState.EXECUTING
        try:
            if asyncio.iscoroutinefunction(task_func):
                res = await task_func(*args, **kwargs)
            else:
                res = task_func(*args, **kwargs)
            ctx.state = LifecycleState.COMPLETED
            return res
        except Exception as e:
            ctx.state = LifecycleState.FAILED
            logger.error(f"Task execution failed [{ctx.request_id}]: {e}")
            raise
        finally:
            async with self._lock:
                self._active_count -= 1
