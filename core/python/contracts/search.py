from typing import Protocol
from dataclasses import dataclass

@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str

class ISearchProvider(Protocol):
    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[SearchResult]:
        ...
