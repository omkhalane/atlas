from typing import Callable, Dict, List
from atlas.core.contracts.event import Event
from atlas.core.runtime.ledger import TransactionLedger

class EventBus:
    def __init__(self, ledger: TransactionLedger):
        self.ledger = ledger
        self.subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Event], None]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event: Event):
        # Persist event
        self.ledger.append(event)
        
        # Notify subscribers
        handlers = self.subscribers.get(event.type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                pass
