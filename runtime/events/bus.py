import asyncio
import json
import logging
from typing import Dict, List, Callable, Awaitable, Any

logger = logging.getLogger("atlas.events")

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[dict], Awaitable[None]]]] = {}
        self.history: List[dict] = []
        self._queue = asyncio.Queue()
        self._running = False

    async def start(self):
        self._running = True
        asyncio.create_task(self._process_events())

    def stop(self):
        self._running = False

    def subscribe(self, event_type: str, handler: Callable[[dict], Awaitable[None]]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    async def publish(self, event_type: str, payload: dict):
        event = {
            "type": event_type,
            **payload
        }
        self.history.append(event)
        await self._queue.put(event)

    async def _process_events(self):
        while self._running:
            event = await self._queue.get()
            event_type = event.get("type")
            
            handlers = self.subscribers.get(event_type, [])
            handlers += self.subscribers.get("*", []) # Catch-all handlers
            
            for handler in handlers:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
                    
            self._queue.task_done()
