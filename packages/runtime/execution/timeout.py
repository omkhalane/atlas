"""
Timeout & Deadline Manager
Enforces strict execution deadlines, timeout limits, retries, and backoff delays per node.
"""
import time
import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger("atlas.execution.timeout")


class TimeoutManager:
    @staticmethod
    async def execute_with_timeout(
        func: Callable[..., Any],
        *args,
        timeout_seconds: float = 30.0,
        max_retries: int = 2,
        backoff_factor: float = 1.5,
        **kwargs
    ) -> Any:
        retries = 0
        current_delay = 1.0
        while True:
            try:
                if asyncio.iscoroutinefunction(func):
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
                else:
                    return await asyncio.wait_for(asyncio.get_event_loop().run_in_executor(None, func, *args), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                logger.warning(f"Execution timed out after {timeout_seconds}s (retry {retries}/{max_retries})")
                if retries >= max_retries:
                    raise TimeoutError(f"Node execution timed out after {max_retries} retries ({timeout_seconds}s limit)")
                retries += 1
                await asyncio.sleep(current_delay)
                current_delay *= backoff_factor
            except Exception as e:
                if retries >= max_retries:
                    raise
                logger.warning(f"Execution failed: {e}. Retrying ({retries}/{max_retries})...")
                retries += 1
                await asyncio.sleep(current_delay)
                current_delay *= backoff_factor
