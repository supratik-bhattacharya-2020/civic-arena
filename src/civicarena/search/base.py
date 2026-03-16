"""Base search provider protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from civicarena.types import SearchResult


@runtime_checkable
class SearchProvider(Protocol):
    """Protocol for pluggable search backends."""

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Execute a search query and return results."""
        ...

    @property
    def name(self) -> str:
        """Human-readable name of this search provider."""
        ...
