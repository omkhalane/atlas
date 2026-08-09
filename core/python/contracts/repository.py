from typing import Protocol

class IAgentStateRepository(Protocol):
    async def save_interaction(self, session_id: str, data: dict) -> None:
        ...
        
    async def get_history(self, session_id: str) -> list[dict]:
        ...
