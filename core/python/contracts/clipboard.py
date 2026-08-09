from typing import Protocol

class IClipboardManager(Protocol):
    async def read_text(self) -> str:
        ...
        
    async def write_text(self, text: str) -> None:
        ...
