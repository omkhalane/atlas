from typing import Protocol

class IBrowserSession(Protocol):
    async def navigate(self, url: str) -> None:
        ...
        
    async def extract_text(self) -> str:
        ...
        
    async def click(self, selector: str) -> None:
        ...
